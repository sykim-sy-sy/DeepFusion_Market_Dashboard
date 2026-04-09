import smtplib
from email.message import EmailMessage
import time
import os
import markdown
import datetime
from dotenv import load_dotenv

# Before using this, please configure the sender email address and App Password.
# In a real environment, it's safer to use environment variables for passwords.
# We are currently loading them from the 'lina_morning_report' .env file if available,
# or defaulting to the hardcoded ones here (as used in send_daily_report.py).

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Load Environment Variables (API Keys, Passwords)
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), "lina_morning_report", ".env")
load_dotenv(ENV_PATH)

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "sykimwk@gmail.com") 
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "igtmaldtdhxqdmsn")  
RECEIVER_EMAIL = ["sykim@deep-fusion.com", "kyujin.lee@deep-fusion.com"]
SUBJECT = f"[Deep Fusion AI] 주간 마켓 및 경쟁사 동향 리포트 (Week {datetime.datetime.now().strftime('%V')})"

def get_latest_weekly_report():
    DATA_DIR = os.path.join(BASE_DIR, "Market_Analyst_Data")
    YEAR_MONTH = datetime.datetime.now().strftime("%Y\\%m")
    TODAY_DIR = os.path.join(DATA_DIR, YEAR_MONTH)
    
    # Construct expected filename for today
    today_str = datetime.datetime.now().strftime('%Y%m%d')
    report_file = os.path.join(TODAY_DIR, f"Weekly_Market_Report_{today_str}.md")

    print(f"Checking for report at: {report_file}")
    
    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except Exception as e:
            return f"Error reading the weekly report: {str(e)}"
    else:
        # Fallback to finding the most recently modified Weekly report in the directory
        if os.path.exists(TODAY_DIR):
            files = [f for f in os.listdir(TODAY_DIR) if f.startswith("Weekly_Market_Report_") and f.endswith(".md")]
            if files:
                # Get the latest one
                files.sort(reverse=True)
                latest_report = os.path.join(TODAY_DIR, files[0])
                print(f"Today's report not found, using latest available: {latest_report}")
                try:
                    with open(latest_report, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    return f"Error reading the weekly report: {str(e)}"
        
        return "No weekly report found for today or this month."

def send_weekly_briefing():
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAIL)
    
    raw_markdown = get_latest_weekly_report()
    
    if "No weekly report found" in raw_markdown or "Error reading" in raw_markdown:
        print(f"Aborting email send: {raw_markdown}")
        return False
        
    html_content = markdown.markdown(raw_markdown, extensions=['tables'])
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
    
    msg.set_content(raw_markdown) 
    msg.add_alternative(html_wrapper, subtype='html')
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Email successfully sent to ({RECEIVER_EMAIL})!")
            return True
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    print("Initiating weekly report email send...")
    success = send_weekly_briefing()
    
    if success:
        print("Weekly report email sent successfully.")
