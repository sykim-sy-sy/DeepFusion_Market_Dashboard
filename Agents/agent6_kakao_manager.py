import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "lina_morning_report", ".env")
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# Parsing Logic
# ---------------------------------------------------------
def parse_kakao_log(file_content):
    """
    Parses KakaoTalk TXT export content into a structured list of messages.
    Supports PC and Mobile formats.
    """
    messages = []
    
    # PC Version Pattern: [Name] [Time] Message
    # Example: [홍길동] [오전 10:01] 회의 시작합시다.
    pc_pattern = r"\[(.+?)\] \[(.+?)\] (.+)"
    
    # Mobile Version Pattern: Date, Time, User, Message (CSV-like)
    # Example: 2026-04-10 10:01, 홍길동 : 회의 시작합시다.
    mobile_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}), (.+?) : (.+)"

    lines = file_content.split('\n')
    current_user = None
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Try PC format
        pc_match = re.match(pc_pattern, line)
        if pc_match:
            user, time_str, text = pc_match.groups()
            messages.append({"user": user, "content": text})
            continue
            
        # Try Mobile format
        mobile_match = re.match(mobile_pattern, line)
        if mobile_match:
            time_str, user, text = mobile_match.groups()
            messages.append({"user": user, "content": text})
            continue
            
        # Append to last message if it's a multi-line message
        if messages:
            messages[-1]["content"] += " " + line

    return messages

# ---------------------------------------------------------
# AI Analysis Logic
# ---------------------------------------------------------
KAKAO_PROMPT = """
당신은 DeepFusion AI의 전문 비즈니스 비서 'Lina'입니다. 
제공된 카카오톡 대화 내역을 바탕으로 다음 실무 요약 보고서를 작성하세요.

[수행 과제]
1. 전체 대화 요약: 어떤 안건들이 논의되었는지 핵심 위주로 요약.
2. 주요 결정 사항: 대화 중 확정된 내용이나 합의된 포인트.
3. 할 일(To-Do) 추출: 담당자(가능한 경우), 기한, 구체적인 액션 아이템을 리스트업.

[응답 형식 (JSON)]
{
  "summary": "전체 논의 내용을 전문적인 어조로 요약 (3-5문장)",
  "decisions": ["결정사항 1", "결정사항 2"],
  "todos": [
    {"task": "업무 내용", "owner": "담당자명", "due": "기한(없으면 '미정')"}
  ]
}
"""

def analyze_chat(file_content):
    if not GEMINI_API_KEY:
        return {"error": "API Key missing"}
    
    # 1. Parse log
    parsed_messages = parse_kakao_log(file_content)
    if not parsed_messages:
        return {"error": "대화 내용을 파싱할 수 없습니다. 형식을 확인해주세요."}
    
    # 2. Limit content size for Gemini (if too large)
    # Strategy: Group by user and join
    chat_blob = ""
    for m in parsed_messages[:500]: # Limit to first 500 messages
        chat_blob += f"{m['user']}: {m['content']}\n"

    # 3. Request Gemini with fallback
    models_to_try = ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-pro']
    last_error = ""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            full_content = f"{KAKAO_PROMPT}\n\n[대화 내역]\n{chat_blob}"
            response = model.generate_content(full_content)
            return json.loads(response.text.strip())
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "quota" in last_error.lower() or "404" in last_error:
                continue # Try next model
            else:
                break
    
    return {"error": f"AI 분석 중 오류 발생: {last_error}"}

if __name__ == "__main__":
    # Test stub
    test_content = "[홍길동] [오전 10:00] 리나야, 4D 레이더 마케팅 리포트 작성해줘.\n[이규진] [오전 10:01] 네, 알겠습니다. 내일까지 보낼게요."
    print(json.dumps(analyze_chat(test_content), indent=2, ensure_ascii=False))
