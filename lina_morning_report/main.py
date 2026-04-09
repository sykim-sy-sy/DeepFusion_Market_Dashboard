import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import feedparser
import google.generativeai as genai
from dotenv import load_dotenv
import urllib.parse
import markdown
import sys
import io
import requests

# Windows 콘솔에서 이모지 출력 시 발생하는 UnicodeEncodeError 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 환경 변수 로드
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "").split(",")
SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "").split(",")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "").strip()

if not GEMINI_API_KEY or not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    print("❌ 환경 변수(.env) 설정이 누락되었습니다. API 키와 이메일 정보를 확인해주세요.")
    print("    팁: '.env.template' 파일의 이름을 '.env'로 바꾸고 안의 내용을 채우셨나요?")
    exit(1)

# 2. 제미나이(Gemini) API 설정
genai.configure(api_key=GEMINI_API_KEY)
# 안정적이고 속도가 빠른 최신 모델 'gemini-2.5-flash' 사용
model = genai.GenerativeModel('gemini-2.5-flash')

def fetch_news(keyword, max_items=5):
    """구글 뉴스 RSS를 통해 특정 키워드의 최신 기사를 가져옵니다. 영문 키워드는 글로벌(미국) 뉴스를 검색합니다."""
    encoded_keyword = urllib.parse.quote(keyword)
    
    # 키워드에 알파벳이 포함되어 있으면 영문(미국) 뉴스로 간주
    is_english = any(c.isalpha() and ord(c) < 128 for c in keyword)
    
    if is_english:
        url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
    else:
        url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
        
    feed = feedparser.parse(url)
    
    news_items = []
    for entry in feed.entries[:max_items]:
        news_items.append(f"- 제목: {entry.title}\n  링크: {entry.link}")
    
    return "\n".join(news_items)

def fetch_data_firecrawl(keyword, max_items=3):
    """Firecrawl API를 통해 키워드와 관련된 심층 정보와 뉴스를 웹 전체에서 검색 및 추출합니다."""
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 영문 키워드인지 확인 후 검색어 보강
    is_english = any(c.isalpha() and ord(c) < 128 for c in keyword)
    query_str = f"{keyword} market news OR technology trends" if is_english else f"{keyword} 시장 동향 최신 뉴스"
    
    payload = {
        "query": query_str,
        "limit": max_items,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code == 200:
            data = response.json()
            items = []
            for item in data.get("data", []):
                title = item.get("title", "제목 없음")
                link = item.get("url", item.get("sourceUrl", ""))
                desc = item.get("description", "")
                
                # 마크다운 내용이 있다면 핵심 요약으로 활용
                content = item.get("markdown", "")
                if content:
                    content_preview = content[:400].replace("\n", " ").strip() + "..."
                else:
                    content_preview = desc
                    
                items.append(f"- 제목: {title}\n  링크: {link}\n  주요내용: {content_preview}")
                
            if items:
                return "\n\n".join(items)
                
        print(f"      [Firecrawl] 실패(상태코드: {response.status_code})하여 일반 뉴스 검색으로 대체합니다.")
        return fetch_news(keyword, max_items)
        
    except Exception as e:
        print(f"      [Firecrawl] 처리 중 오류({e})가 발생하여 일반 뉴스 검색으로 대체합니다.")
        return fetch_news(keyword, max_items)

def generate_report(news_data):
    """가져온 리서치 자료를 바탕으로 리나(AI)가 보고서를 작성합니다."""
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""
당신은 '딥퓨전에이아이(Deepfusion AI)'의 10년 차 수석 시장 분석가 '리나(Lina)'입니다.
당신은 B2B 시장(자율주행, 4D 이미징 레이더, 스마트시티, 로보틱스, 산업용 장비 등)의 트렌드와 경쟁 우위를 꿰뚫어보는 날카로운 통찰력을 가졌습니다.

다음은 오늘 아침 수집된 국내 및 글로벌 최신 심층 웹 리서치/뉴스 데이터입니다:
{news_data}

위 데이터를 분석하여 마케팅 팀과 경영진이 읽기 편하도록 아래의 양식에 맞추어 마크다운(Markdown) 포맷으로 예쁘게 작성해주세요. 
우리 회사의 비즈니스에 영향이 있는 핵심 내용만 추려내고, 반드시 **국내 뉴스와 글로벌(해외) 뉴스를 모두 골고루 포함**하여 3가지를 선정하세요.

[보고서 양식 작성 가이드]
# [리포트] 오늘의 아침 브리핑 ({today})

## 1️⃣ 짚고 넘어갈 주요 3가지 이슈
(국내/해외 소식을 균형있게 포함하여 가장 중요한 이슈 3가지를 브리핑. 반드시 각 이슈마다 **[기사 원문 보기](원본 링크 URL)** 형식으로 출처 링크를 달아주세요. 왜 이게 중요한지도 설명.)

## 2️⃣ 시장 및 경쟁사 동향
(업계 탑티어 분석가 관점에서 글로벌 트렌드 요약)

## 3️⃣ 우리의 Action Point
(딥퓨전에이아이가 취할 수 있는 현실적이고 실무적인 액션 제안 1~2줄)
"""
    print("🧠 리나가 가져온 뉴스를 분석하고 있습니다...")
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, markdown_content):
    """분석된 보고서를 마크다운 형태로 메일 발송합니다."""
    print("📧 이메일 발송을 준비합니다...")
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    
    # 여러 수신자 처리
    valid_emails = [e.strip() for e in RECIPIENT_EMAILS if e.strip()]
    if not valid_emails:
        print("❌ 수신자 이메일 주소가 없습니다. .env 파일을 확인하세요.")
        return
        
    msg['To'] = ", ".join(valid_emails)
    msg['Subject'] = subject
    # 링크와 기타 마크다운 문법이 HTML 태그 안에서도 완벽히 변환되도록 확장(extensions) 추가
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'nl2br', 'fenced_code'])
    
    styled_html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333; }}
          h1 {{ color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 5px; }}
          h2 {{ color: #2980B9; margin-top: 20px; }}
          p {{ margin-bottom: 10px; }}
          li {{ margin-bottom: 5px; }}
          a {{ color: #3498DB; text-decoration: none; }}
          a:hover {{ text-decoration: underline; }}
        </style>
      </head>
      <body>
        <div style="background-color: #F8F9FA; padding: 20px; border-radius: 8px;">
            {html_content}
        </div>
        <p style="margin-top: 30px; font-size: 11px; color: #7F8C8D;">※ 본 메일은 리나 아침 보고 자동화 봇에 의해 발송되었습니다.</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(styled_html, 'html'))
    
    try:
        # TLS 보안 연결 설정 (권장 방식)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 이메일 발송 완료! (수신자: {', '.join(valid_emails)})")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 아침 보고 시스템 가동")
    
    all_news_data = ""
    for keyword in SEARCH_KEYWORDS:
        keyword = keyword.strip()
        if not keyword or keyword == "키워드1" or keyword == "키워드2": 
            continue
            
        print(f"🔍 '{keyword}' 관련 리서치를 수행 중입니다...")
        if FIRECRAWL_API_KEY:
            print("   👉 Firecrawl 엔진을 사용하여 시장 동향을 심층 수집합니다.")
            news = fetch_data_firecrawl(keyword)
        else:
            news = fetch_news(keyword)
            
        if news:
            all_news_data += f"\n--- [{keyword}] 관련 심층 데이터 ---\n{news}\n"
    
    if not all_news_data.strip():
        print("❌ 수집된 뉴스가 없습니다. 키워드 설정을 확인하시거나, 연관 뉴스가 아직 없는 것일 수 있습니다.")
        exit(0)
    
    # 리포트 생성
    report_content = generate_report(all_news_data)
    
    # 오늘 날짜를 활용해 제목 생성
    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    subject = f"[리포트] 오늘의 아침 브리핑 - {today_str}"
    
    # 이메일 전송
    send_email(subject, report_content)
    print("🎉 아침 보고 프로세스가 모두 성공적으로 끝났습니다!")
