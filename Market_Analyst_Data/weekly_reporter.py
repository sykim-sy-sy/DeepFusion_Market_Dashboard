import os
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# ==============================================================================
# 🕵️ 시장/경쟁사 분석관 - 주간 리포트 발행 스크립트 (매주 수요일 실행)
# ==============================================================================

# 1. 환경 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Market_Analyst_Data")
YEAR_MONTH = datetime.datetime.now().strftime("%Y\\%m")
TODAY_DIR = os.path.join(DATA_DIR, YEAR_MONTH)

# 읽어올 Raw 데이터 파일 (이번 주 파일)
WEEK_NUM = datetime.datetime.now().strftime('%V')
RAW_DATA_FILE = os.path.join(TODAY_DIR, f"weekly_raw_data_{WEEK_NUM}week.md")

# 발행할 최종 리포트 파일
REPORT_FILE = os.path.join(TODAY_DIR, f"Weekly_Market_Report_{datetime.datetime.now().strftime('%Y%m%d')}.md")

# `.env` 폴더 경로 및 Gemini API 설정
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), "lina_morning_report", ".env")
load_dotenv(ENV_PATH)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ 경고: GEMINI_API_KEY를 찾을 수 없어 리포트를 생성할 수 없습니다.")
    exit(1)

# 2. 리포트 작성 프롬프트 템플릿
REPORT_PROMPT = """
당신은 딥퓨전에이아이(Deepfusion AI)의 최고 시장 분석가입니다.
아래 제공된 [이번 주 수집된 Raw Data]를 분석하여 당사 경영진을 위한 전략적 주간 리포트를 작성해주세요.
반드시 한국어로 작성하세요.

[이번 주 수집된 Raw Data]
{raw_data}

[🚨 작성 지침 - 절대 준수]
1. **완벽한 개조식(Bullet Point) 필수**: 모든 문장은 명사형 어미(~~함, ~~임, ~~예정, ~~공개)로 끝맺음하세요. **~합니다, ~입니다와 같은 서술형 문장 및 종결어미는 100% 절대 사용 금지**입니다.
    - (나쁜 예): 우리 회사는 Tier-1과 협력합니다.
    - (좋은 예): 글로벌 Tier-1 파트너십 확대를 통한 시장 지배력 강화
2. 분석 대상은 최근 1주일 이내 뉴스 기반 필수.
3. **회사 구분**: **딥퓨전에이아이(Deepfusion AI)**는 '우리 회사'이므로 경쟁사(Competitor) 목록에서 완전 제외.
4. **시각적 자료**: Mermaid 차트 활용 필수.
5. **링크 정확성**: Raw Data의 원본 링크 절대 유지.
6. **섹션 구성**:
    - **Executive Summary**: 주간 핵심 요약 3가지 (개조식)
    - **Internal Status**: 딥퓨전에이아이 성과/행보 (개조식)
    - **Technology & Market Trends**: 시장 동향 및 기회 분석 (개조식)
    - **Competitor Analysis**: Aptiv 등 실제 경쟁사 동향 (개조식)
    - **Actionable Insight**: 실행 아이템 제안 (개조식)

비고: 'Technology & Market Trends'와 'Competitor Analysis'는 서로 섞이지 않도록 명확한 헤더(##)를 사용하여 분리하세요. 
보고서는 전문적이고 통찰력 있는 톤앤매너를 유지해야 합니다.
"""

def generate_weekly_report():
    print(f"[시장/경쟁사 분석관] 주간 리포트 작성 시작 ({datetime.datetime.now()})")
    
    # 1. Raw 데이터 읽기
    if not os.path.exists(RAW_DATA_FILE):
        print(f"오류: 이번 주 누적 데이터 파일을 찾을 수 없습니다. ({RAW_DATA_FILE})")
        return
        
    with open(RAW_DATA_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        raw_content = f.read()

    print(f" -> Raw 데이터 로드 완료 ({len(raw_content)} bytes)")

    # 2. Gemini API를 통해 분석 및 리포트 작성
    print(" -> Gemini AI 모델로 요약 리포트 작성 중...")
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # 프롬프트에 현재 날짜 정보를 동적으로 삽입하여 recency 강조
        today_info = datetime.datetime.now().strftime("%Y-%m-%d")
        week_ago_info = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        
        dynamic_prompt = REPORT_PROMPT.format(raw_data=raw_content)
        # 위 템플릿의 지침 2번을 동적으로 업데이트
        dynamic_prompt = dynamic_prompt.replace("2026-03-04 ~ 2026-03-11", f"{week_ago_info} ~ {today_info}")
        
        response = model.generate_content(dynamic_prompt)
        
        final_report = f"# 📈 Weekly Market & Competitor Report (Week {WEEK_NUM})\n\n"
        final_report += f"*발행일: {datetime.datetime.now().strftime('%Y-%m-%d')}*\n\n"
        final_report += response.text
    except Exception as e:
        print(f"Gemini API 에러: {e}")
        return

    # 3. 리포트 파일 저장
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_report)
        
    print(f"주간 리포트 발행 완료! (저장 위치: {REPORT_FILE})")

if __name__ == "__main__":
    generate_weekly_report()
