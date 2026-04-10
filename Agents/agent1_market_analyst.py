import os
import smtplib
import json
import time
import sys
import io
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
import requests
import re
import argparse

# Windows 콘솔에서 이모지 출력 백업
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "Market_Analyst_Data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"lina_log_{datetime.now().strftime('%Y%m%d')}.txt")

# DB 모듈 로드
sys.path.append(BASE_DIR)
try:
    from Market_Analyst_Data import db_manager
except ImportError:
    pass # If running from other places it might fail, fallback gracefully

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

log("Lina (V2 - 1:1 Deep Analysis) starts initialization...")

# ---------------------------------------------------------
# Agent Configuration Settings
# ---------------------------------------------------------
ENV_PATH = os.path.join(BASE_DIR, "lina_morning_report", ".env")
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAILS = [
    "sykim@deep-fusion.com",            
    "kyujin.lee@deep-fusion.com"       
]
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "").strip()

# 무의미한 정보가 많은 도메인 블랙리스트
DOMAIN_BLACKLIST = [
    "zhihu.com", "reddit.com", "quora.com", "forum.wordreference.com", 
    "youtube.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "naver.com/cafe", "daum.net/cafe", "fmkorea.com", "ruliweb.com", "inven.co.kr"
]

# 시장/기술 동향 분석을 위한 광범위 키워드
INDUSTRY_KEYWORDS = [
    "4D Imaging Radar Market News", 
    "Autonomous Driving Sensor Technology Trends",
    "Automotive Radar Industry Analysis",
    "ADAS perception software innovation"
]

# ---------------------------------------------------------
# Prompt & Parsing Configuration
# ---------------------------------------------------------
NEW_LINA_SYSTEM_PROMPT = """
당신은 'Lina(리나)'이며, 자율주행 및 4D 이미징 레이더 전문 센서 기업 '딥퓨전에이아이(DeepFusion AI)'의 수석 시장 분석가입니다.
제공된 [분석 대상]의 수집 데이터와 [URL 후보 리스트]를 바탕으로 다음의 JSON 형식으로만 응답하세요. 

지침:
1. 데이터가 비어있거나 무의미하다면 "새로운 동향 없음"이라고 명확히 표기하세요. 
2. 절대로 없는 사실이나 가짜 링크를 만들어내지 마세요.
3. 'selected_sources'에는 제공된 [URL 후보 리스트] 중 당신이 도출한 'facts'와 'implications'를 가장 잘 뒷받침하는 핵심 소스 링크 3~5개만 선별하여 포함하세요.

응답 형식 (JSON만 출력):
{
  "facts": "발생한 핵심 팩트를 개조식(Bullet point)으로 요약.",
  "implications": "당사(딥퓨전 AI)에 주는 위협, 기회 또는 Action Point 도출",
  "selected_sources": ["https://url1.com", "https://url2.com"]
}
"""

TARGET_LIST_PATH = os.path.join(BASE_DIR, "Market_Analyst_Data", "target_monitoring_list.md")

# ---------------------------------------------------------
# Core Helper Functions
# ---------------------------------------------------------

def load_target_competitors():
    if not os.path.exists(TARGET_LIST_PATH):
        log(f"Target list not found at {TARGET_LIST_PATH}!")
        return []
    
    competitors = []
    try:
        with open(TARGET_LIST_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("| **"):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        name = parts[1].replace("**", "")
                        url = parts[3]
                        competitors.append({"name": name, "url": url})
    except Exception as e:
        log(f"Error loading target list: {e}")
    return competitors

def fetch_data_firecrawl(keyword, url_to_scrape=None):
    if not FIRECRAWL_API_KEY: return None
    api_url = "https://api.firecrawl.dev/v1/scrape" if url_to_scrape else "https://api.firecrawl.dev/v1/search"
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
    payload = {"formats": ["markdown"], "onlyMainContent": True}
    
    if url_to_scrape:
        payload["url"] = url_to_scrape
    else:
        payload["query"] = f"{keyword} latest technology business news"
        payload["limit"] = 3

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200: return resp.json()
    except Exception as e:
        log(f"Firecrawl error: {e}")
    return None

def fetch_structured_news(keyword, time_limit='w'):
    """뉴스 데이터와 링크 리스트를 튜플 분리 형태로 반환: (문자열 리포트, URL 목록)"""
    extracted_urls = []
    news_text = ""
    
    if FIRECRAWL_API_KEY:
        api_url = "https://api.firecrawl.dev/v1/search"
        headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
        time_text = "last 24 hours" if time_limit == 'd' else "last 7 days"
        try:
            resp = requests.post(api_url, headers=headers, json={"query": f"{keyword} {time_text} news technology", "limit": 4}, timeout=30)
            if resp.status_code == 200:
                results = resp.json().get("data", [])
                if results:
                    mapped = []
                    for r in results:
                        url = r.get('url')
                        if url:
                            # Blacklist filter
                            if any(bad in url.lower() for bad in DOMAIN_BLACKLIST):
                                continue
                            extracted_urls.append(url)
                            mapped.append(f"- 제목: {r.get('title')}\n  요약: {r.get('description')}\n  URL: {url}")
                    news_text = "\n\n".join(mapped)
                    return news_text, extracted_urls
        except Exception as e:
            log(f"Firecrawl Search error: {e}")

    # Fallback to DDGS Text
    log(f"   (Search) Using fallback DuckDuckGo Text search for {keyword}...")
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            time_filter = 'd' if time_limit == 'd' else 'w'
            results = list(ddgs.text(f"{keyword} news", max_results=4, timelimit=time_filter))
            news_items = []
            for r in results:
                url = r.get('href')
                if url:
                    # Blacklist filter
                    if any(bad in url.lower() for bad in DOMAIN_BLACKLIST):
                        continue
                    extracted_urls.append(url)
                    news_items.append(f"- 제목: {r.get('title')}\n  요약: {r.get('body')}\n  URL: {url}")
            
            if not news_items:
                return "최근 새 뉴스가 없습니다.", []
            news_text = "\n\n".join(news_items)
            return news_text, extracted_urls
    except Exception as e:
        log(f"DDGS Text search error: {e}")
    
    return "", []

def analyze_single_competitor(comp_name, raw_data, retries=2):
    """1:1 밀착 분석 (JSON Format)"""
    if not GEMINI_API_KEY:
        return {"facts": "API Key missing", "implications": "API Key missing"}
    
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    for model_name in models_to_try:
        for i in range(retries + 1):
            try:
                clean_model_name = model_name.replace('models/', '')
                model = genai.GenerativeModel(clean_model_name, generation_config={"response_mime_type": "application/json", "temperature": 0.2})
                
                # 원본 URL 리스트를 함께 제공하여 AI가 선택하게 함
                url_list_str = "\n".join(list(set(raw_data.get("urls", [])))) if isinstance(raw_data, dict) else ""
                content_blob = raw_data.get("content", raw_data) if isinstance(raw_data, dict) else raw_data
                
                full_prompt = f"{NEW_LINA_SYSTEM_PROMPT}\n\n[분석 대상: {comp_name}]\n\n[URL 후보 리스트]\n{url_list_str}\n\n[수집된 데이터 콘텐츠]\n{content_blob}"
                response = model.generate_content(full_prompt)
                
                result = json.loads(response.text.strip())
                return {
                    "facts": result.get("facts", ""), 
                    "implications": result.get("implications", ""),
                    "selected_sources": result.get("selected_sources", [])
                }
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    time.sleep(15) # Wait and continue
                    continue
                else: # Model JSON failure or Not found
                    break 
    return {"facts": "분석 실패", "implications": "AI 엔진 응답 없음"}

# ---------------------------------------------------------
# Runner Execution
# ---------------------------------------------------------

def run_agent(forced_mode=None):
    log("==================================================")
    log("🕵️ Lina (V2) Market Analyst Engine Running...")
    log(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("==================================================")
    
    # DB 초기화
    try:
        db_manager.init_db()
        log("Database initialized successfully.")
    except Exception as e:
        log(f"DB Init Error: {e}")

    if forced_mode:
        is_monday = (forced_mode.lower() == "weekly")
    else:
        is_monday = (datetime.now().weekday() == 0)

    report_type = "주간 심층 분석" if is_monday else "데일리 브리핑"
    time_limit = 'w' if is_monday else 'd'

    competitors = load_target_competitors()
    if not competitors:
        log("No competitors to monitor. Exiting.")
        return

    final_report_sections = []
    
    # ---------------------------------------------------------
    # PART 1. Global Market & Tech Trend Analysis
    # ---------------------------------------------------------
    market_trend_sections = []
    log(" -> Performing Global Market & Tech Trend Analysis...")
    
    combined_market_news = ""
    combined_market_urls = []
    
    for m_kw in INDUSTRY_KEYWORDS:
        news_text, news_urls = fetch_structured_news(m_kw, time_limit=time_limit)
        if news_text and "새 뉴스가 없습" not in news_text:
            combined_market_news += f"--- Keyword: {m_kw} ---\n{news_text}\n\n"
            combined_market_urls.extend(news_urls)
            
    if combined_market_news:
        # URL 리스트를 포함하여 분석 요청
        raw_bundle = {"content": combined_market_news, "urls": list(set(combined_market_urls))}
        market_res = analyze_single_competitor("시장 및 기술 동향", raw_bundle)
        
        if "새로운 동향 없음" not in market_res['facts']:
            category_name = "시장 및 기술 동향"
            selected_links = market_res.get('selected_sources', [])
            
            # DB Save (AI가 선별한 링크만 저장)
            try:
                final_urls_str = "\n".join(selected_links)
                db_manager.insert_analysis(category_name, market_res['facts'], market_res['implications'], final_urls_str)
            except Exception as e:
                log(f"    Market Trend DB Insert Error: {e}")
            
            # Form section for email
            links_md = ""
            for u in selected_links:
                links_md += f"- {u}\n"
            if not links_md: links_md = "- 관련 고품질 링크 없음"
            
            section = f"### 🌐 {category_name}\n\n**[📌 주요 동향]**\n{market_res['facts']}\n\n**[💡 DeepFusion 시사점]**\n{market_res['implications']}\n\n**[🔗 관련 소스]**\n{links_md}\n\n---\n"
            market_trend_sections.append(section)
            log("    Successfully captured global market trends with AI-filtered sources.")
    else:
        log("    No significant global market trends found today.")

    # ---------------------------------------------------------
    # PART 2. Specific Competitor Deep Dive
    # ---------------------------------------------------------
    competitor_sections = []
    for comp in competitors:
        comp_name = comp['name']
        log(f" -> 1:1 Deep Dive Analysis for {comp_name}...")
        
        # 1. Fetch data
        site_data = fetch_data_firecrawl(None, comp['url'])
        site_content = site_data.get("data", {}).get("markdown", "")[:500] if site_data and site_data.get("success") else ""
        
        news_text, news_urls = fetch_structured_news(comp_name, time_limit=time_limit)
        
        if not site_content and ("새 뉴스가 없습" in news_text or not news_text):
            log(f"    (Skipping {comp_name} - No meaningful updates)")
            continue
            
        raw_blob = f"홈페이지 요약:\n{site_content}\n\n외부 뉴스 요약:\n{news_text}"
        raw_bundle = {"content": raw_blob, "urls": list(set(news_urls))}
        
        # 2. Analyze per competitor
        ai_res = analyze_single_competitor(comp_name, raw_bundle)
        
        if "새로운 동향 없음" in ai_res['facts'] or "새로운 동향 없음" in ai_res['implications']:
            log(f"    (Skipping {comp_name} - AI found no meaningful insights)")
            continue
            
        selected_links = ai_res.get('selected_sources', [])
        
        # 3. DB Save
        final_urls_str = "\n".join(selected_links)
        try:
            db_manager.insert_analysis(comp_name, ai_res['facts'], ai_res['implications'], final_urls_str)
        except Exception as e:
            log(f"    DB Insert Error: {e}")
            
        # 4. Append to final mail report
        links_markdown = ""
        for u in selected_links:
            links_markdown += f"- {u}\n"
        if not links_markdown: links_markdown = "- 관련 고품질 링크 없음"

        section = f"### 🏢 {comp_name}\n\n**[📌 팩트 체크]**\n{ai_res['facts']}\n\n**[💡 DeepFusion 시사점]**\n{ai_res['implications']}\n\n**[🔗 링크]**\n{links_markdown}\n\n---\n"
        competitor_sections.append(section)
        
        time.sleep(2) # 부하 관리

    # 취합 후 결과 발송
    today = datetime.now().strftime("%Y-%m-%d")
    final_report_sections = market_trend_sections + competitor_sections
    
    if not final_report_sections:
        final_body = "모니터링한 경쟁사 및 시장 동향에 대해 오늘 수집된 유의미한 변동 사항이나 새로운 뉴스가 없습니다."
    else:
        final_body = "\n".join(final_report_sections)

    report_content = f"""
# 📊 {report_type} 리포트 (Lina V2)
*작성일: {today}*
*업데이트: 각 경쟁사별 1:1 심층 분석(So What 프레임워크) 및 거짓 링크 필터링 적용 개편판*

{final_body}
"""
    
    # 이메일 발송
    email_subject = f"[Lina] {report_type} ({today}) - V2"
    send_email_report(report_content, subject=email_subject)
    
    log(f"\n✅ Lina's V2 {report_type} cycle finished successfully.")

def send_email_report(report_content, subject=None):
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        log("Email credentials missing. Skipping email.")
        return
    
    log(f"\n[Email] Sending report to {', '.join(RECIPIENT_EMAILS)}...")
    today = datetime.now().strftime("%Y-%m-%d")
    final_subject = subject if subject else f"[Lina] 마켓 분석 리포트 ({today})"
    
    msg = MIMEMultipart()
    msg['Subject'] = final_subject
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENT_EMAILS)
    
    html_content = markdown.markdown(report_content, extensions=['tables', 'nl2br'])
    
    final_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #004b87; border-bottom: 3px solid #004b87; padding-bottom: 10px; font-size: 24px; }}
            h2 {{ color: #005a9c; margin-top: 30px; border-left: 5px solid #005a9c; padding-left: 10px; font-size: 20px; }}
            h3 {{ color: #424242; margin-top: 20px; font-size: 18px; }}
            a {{ color: #0066cc; text-decoration: none; font-weight: bold; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            {html_content}
            <div class="footer">
                본 리포트는 DeepFusion AI 마케팅 에이전트 'Lina V2'에 의해 자동 생성, 데이터베이스 보관 및 발송되었습니다.
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(final_html, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        log("✅ Email sent successfully!")
    except Exception as e:
        log(f"❌ Email sending failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lina Market Analyst Agent V2")
    parser.add_argument("--daily", action="store_true", help="Force run daily report")
    parser.add_argument("--weekly", action="store_true", help="Force run weekly report")
    args = parser.parse_args()

    mode = None
    if args.daily: mode = "daily"
    elif args.weekly: mode = "weekly"

    run_agent(forced_mode=mode)
