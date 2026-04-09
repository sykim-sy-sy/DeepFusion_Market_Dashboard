import streamlit as st
import pandas as pd
import sqlite3
import os

# 페이지 기본 설정
st.set_page_config(page_title="DeepFusion AI 마켓 대시보드", page_icon="📡", layout="wide")

# CSS 스타일링 추가 (Aesthetics)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #004b87;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 30px;
    }
    .fact-box {
        background-color: #f8fbff;
        padding: 20px;
        border-left: 5px solid #005a9c;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .insight-box {
        background-color: #fff9c4;
        padding: 20px;
        border-left: 5px solid #fbc02d;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 DeepFusion AI 모닝 인사이트 데스크</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI 에이전트 Lina가 매일 수집 및 심층 분석하는 자율주행 센서/4D 레이더 경쟁사 동향 대시보드입니다.</p>', unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "market_data.db")

@st.cache_data(ttl=60) # 1분마다 캐시 갱신
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM competitor_analysis ORDER BY report_date DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"데이터베이스 로딩 오류: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("📌 아직 수집된 데이터가 없습니다. Lina의 자동화 에이전트가 실행되면 여기에 분석 데이터가 차곡차곡 쌓이게 됩니다.")
else:
    # ---------------------------------------------------------
    # 왼쪽 사이드바 (필터)
    # ---------------------------------------------------------
    st.sidebar.header("🔍 데이터 필터 탐색기")
    st.sidebar.write("보고 싶은 조건만 골라서 필터링하세요.")
    
    companies = ["전체 조회"] + list(df['competitor'].unique())
    selected_company = st.sidebar.selectbox("🏢 특정 경쟁사 집중 보기", companies)
    
    dates = ["전체 날짜"] + list(df['report_date'].unique())
    selected_date = st.sidebar.selectbox("📆 특정 날짜 리포트 보기", dates)
    
    # ---------------------------------------------------------
    # 데이터 필터링 적용
    # ---------------------------------------------------------
    filtered_df = df.copy()
    if selected_company != "전체 조회":
        filtered_df = filtered_df[filtered_df['competitor'] == selected_company]
    if selected_date != "전체 날짜":
        filtered_df = filtered_df[filtered_df['report_date'] == selected_date]
        
    # === [신규 추가] 시각화 요약(KPI) ===
    st.markdown("### 📈 전체 시장 동향 한눈에 보기")
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="총 누적 분석 리포트", value=f"{len(df)}건")
    with m2:
        st.metric(label="보유 중인 수집 타겟 풀", value=f"{df['competitor'].nunique()}개 기업 단위")
        
    st.divider()
    # =========================================

    st.subheader(f"📑 타겟 분석 타임라인: 검색된 리포트 총 {len(filtered_df)}건")
    st.write("발생 일자별로 최신순 정렬된 분석 리포트입니다.")

    # ---------------------------------------------------------
    # 메인 리포트 렌더링 (일자별 타임라인 그룹핑)
    # ---------------------------------------------------------
    current_date = None
    
    for index, row in filtered_df.iterrows():
        date = row['report_date']
        comp = row['competitor']
        
        # 날짜가 바뀌었을 때 날짜 구분선을 크고 명확하게 표시
        if date != current_date:
            st.markdown(f"<br><h2 style='color: #4A90E2;'>📅 {date}</h2>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-top: 2px solid #4A90E2;'>", unsafe_allow_html=True)
            current_date = date
            
        with st.expander(f"🏢 {comp} 인사이트 리포트", expanded=(index==0)):
            
            st.markdown("### 🔎 팩트 체크 (사실 관계)")
            st.markdown(f'<div class="fact-box">{row["facts"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 💡 우리 회사에 주는 시사점 (위협 및 기회)")
            st.markdown(f'<div class="insight-box">{row["implications"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🔗 원문 출처 (검증된 링크)")
            if row['urls'] and str(row['urls']).strip():
                urls = str(row['urls']).split('\n')
                for u in urls:
                    u = u.strip()
                    if u:
                        st.markdown(f"👉 [{u}]({u})")
            else:
                st.caption("제공된 외부 기사 링크가 없습니다.")
