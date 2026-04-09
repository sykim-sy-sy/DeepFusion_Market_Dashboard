import sqlite3
import os
from datetime import datetime

# 데이터베이스 파일 경로 (현재 폴더의 market_data.db)
DB_PATH = os.path.join(os.path.dirname(__file__), "market_data.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """데이터베이스와 테이블을 생성합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitor_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,
            competitor TEXT,
            facts TEXT,
            implications TEXT,
            urls TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_analysis(competitor, facts, implications, urls):
    """
    AI가 분석한 결과를 DB에 저장합니다.
    동일한 날짜에 같은 경쟁사를 여러 번 분석할 경우 기존 기록을 덮어씁니다.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 오늘 날짜의 동일 경쟁사 데이터가 있다면 덮어쓰기 위해 기존 데이터 삭제
    cursor.execute('''
        DELETE FROM competitor_analysis 
        WHERE report_date = ? AND competitor = ?
    ''', (today, competitor))
    
    # 새 데이터 추가
    cursor.execute('''
        INSERT INTO competitor_analysis (report_date, competitor, facts, implications, urls)
        VALUES (?, ?, ?, ?, ?)
    ''', (today, competitor, facts, implications, urls))
    
    conn.commit()
    conn.close()

def fetch_all_data():
    """웹 대시보드에서 조회하기 위해 모든 데이터를 불러옵니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT report_date, competitor, facts, implications, urls FROM competitor_analysis ORDER BY report_date DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("✅ 데이터베이스가 성공적으로 초기화되었습니다:", DB_PATH)
