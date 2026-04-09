import smtplib
from email.message import EmailMessage
import time
import os
import markdown
import base64
import re

# Before using this, please configure the sender email address and App Password.

SENDER_EMAIL = "sykimwk@gmail.com" # 팀장님 또는 리나 계정
SENDER_PASSWORD = "igtmaldtdhxqdmsn" # 구글/아웃룩 앱 비밀번호 입력 필요
RECEIVER_EMAIL = ["sykim@deep-fusion.com", "kyujin.lee@deep-fusion.com"]
SUBJECT = "[Deep Fusion AI] 일일 기술/시장 전략 브리핑"

def get_briefing_content():
    # 예시 경로 처리 
    file_path = r"C:\Users\KIM SIYE\.gemini\antigravity\brain\4046b489-5cae-4141-8acf-fc0423d7efa0\daily_briefing_20260306.md"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception as e:
        return f"보고서를 불러오는데 실패했습니다: {str(e)}"

def embed_images(html_str):
    def replace_img(match):
        img_src = match.group(1)
        if os.path.exists(img_src):
            with open(img_src, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                ext = "png"
                if img_src.lower().endswith(('.jpg', '.jpeg')): ext = "jpeg"
                return f'src="data:image/{ext};base64,{encoded_string}"'
        return match.group(0)
    
    return re.sub(r'src=["\']([^"\']+)["\']', replace_img, html_str)

def send_daily_briefing():
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAIL)
    
    raw_markdown = get_briefing_content()
    
    # CSS 스타일을 적용한 HTML 변환
    html_content = markdown.markdown(raw_markdown, extensions=['tables'])
    html_content = embed_images(html_content)
    html_wrapper = f"""
    <html>
    <head>
    <style>
        body {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333; }}
        h1 {{ color: #004b87; border-bottom: 2px solid #004b87; padding-bottom: 5px; }}
        h2 {{ color: #005a9c; margin-top: 25px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f4f7f6; color: #333; }}
        a {{ color: #0066cc; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        .mermaid {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #004b87; font-family: monospace; white-space: pre; overflow-x: auto; }}
        code {{ background-color: #f1f1f1; padding: 2px 4px; border-radius: 4px; }}
    </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # 텍스트와 HTML 본문 모두 설정하여 가독성 강화
    msg.set_content(raw_markdown) # 대체 텍스트
    msg.add_alternative(html_wrapper, subtype='html')
    
    # Send email (Google SMTP example)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 팀장님({RECEIVER_EMAIL})께 이메일 전송 성공! (HTML 버전)")
            return True
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 전송 실패: {str(e)}")
        return False

# Test run immediately (시범 발송)
if __name__ == "__main__":
    print("Test HTML email run initiated...")
    success = send_daily_briefing()
    
    if success:
        print("HTML 포맷 시범 발송이 완료되었습니다.")

