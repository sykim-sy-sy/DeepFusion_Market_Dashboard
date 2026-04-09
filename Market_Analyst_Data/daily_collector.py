import os
import json
import datetime
from zoneinfo import ZoneInfo
import requests
from duckduckgo_search import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

# ==============================================================================
# 🕵️ 시장/경쟁사 분석관 (Market & Competitor Analyst) - 데일리 수집 스크립트
# ==============================================================================

# 1. 환경 설정 (경로 및 API 키)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Market_Analyst_Data")
YEAR_MONTH = datetime.datetime.now().strftime("%Y\\%m")
TODAY_DIR = os.path.join(DATA_DIR, YEAR_MONTH)

os.makedirs(TODAY_DIR, exist_ok=True)

# `.env` 폴더 경로 (기존 lina_morning_report 폴더의 .env 활용)
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), "lina_morning_report", ".env")
load_dotenv(ENV_PATH)

RAW_DATA_FILE = os.path.join(TODAY_DIR, f"weekly_raw_data_{datetime.datetime.now().strftime('%V')}week.md")

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ 경고: GEMINI_API_KEY를 .env 파일에서 찾을 수 없습니다. 요약 기능이 작동하지 않습니다.")

# 2. 타겟 키워드 및 URL 리스트 (추후 target_monitoring_list.md 에서 동적으로 불러오는 형태로 고도화 가능)
TARGET_KEYWORDS = ["4D Imaging Radar", "Deepfusion AI", "Aptiv Radar", "Oculii", "Bitsensing"]

def fetch_news(keyword):
    """지정된 키워드로 뉴스를 검색합니다 (최근 7일 이내 기사만 수집)."""
    try:
        articles = []
        now = datetime.datetime.now(datetime.timezone.utc)
        seven_days_ago = now - datetime.timedelta(days=7)
        
        with DDGS() as ddgs:
            # timelimit='w'를 추가하여 검색 단계에서부터 최근 1주일 기사로 제한
            results = ddgs.news(keyword, max_results=10, timelimit='w') 
            for r in results:
                date_str = r.get('date')
                if date_str:
                    article_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    if article_date < seven_days_ago:
                        continue
                
                articles.append({
                    "title": r.get('title', ''), 
                    "link": r.get('url', ''), 
                    "date": date_str if date_str else datetime.datetime.now().isoformat()
                })
        return articles[:5] # 충분한 최신 기사 확보를 위해 최대 5개 반환
    except Exception as e:
        print(f"[{keyword}] 뉴스 수집 실패: {e}")
        return []

def summarize_with_gemini(text):
    """(선택 사항) Gemini를 사용해 긴 기사를 3줄로 요약합니다."""
    if not GEMINI_API_KEY:
        return "요약 불가 (API 키 없음)"
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"다음 뉴스 제목이나 내용을 딥퓨전에이아이 마케터 관점에서 한국어로 짧게 1줄 요약해줘: {text}")
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API 에러: {e}")
        return "요약 실패"

def run_daily_collection():
    print(f"[시장/경쟁사 분석관] 데일리 뉴스 수집 시작 ({datetime.datetime.now()})")
    
    all_news = {}
    for kw in TARGET_KEYWORDS:
        print(f" -> '{kw}' 뉴스 검색 중...")
        articles = fetch_news(kw)
        if articles:
            all_news[kw] = articles
            
    # 파일에 기록
    file_exists = os.path.exists(RAW_DATA_FILE)
    mode = 'a' if file_exists else 'w'
    
    with open(RAW_DATA_FILE, mode, encoding='utf-8') as f:
        if not file_exists:
            f.write(f"# 시장 및 경쟁사 동향 Raw Data (Week {datetime.datetime.now().strftime('%V')})\n\n")
            f.write("> 본 문서는 매일 수집된 뉴스 타이틀과 링크가 누적되는 로컬 위키 데이터베이스입니다.\n\n")
            
        today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        f.write(f"## 수집일: {today_str}\n\n")
        
        for kw, articles in all_news.items():
            f.write(f"### 키워드: {kw}\n")
            for idx, art in enumerate(articles, 1):
                f.write(f"{idx}. [{art['title']}]({art['link']})\n")
                f.write(f"   - 💡 요약: {summarize_with_gemini(art['title'])}\n")
                
        f.write("\n---\n\n")
        
    print(f"완료! 데이터가 성공적으로 누적되었습니다. (위치: {RAW_DATA_FILE})")

if __name__ == "__main__":
    run_daily_collection()
