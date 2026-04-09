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
    
    # ---------------------------------------------------------
    # 데이터 필터링 적용 (특정 경쟁사)
    # ---------------------------------------------------------
    filtered_df = df.copy()
    if selected_company != "전체 조회":
        filtered_df = filtered_df[filtered_df['competitor'] == selected_company]
        
    unique_dates = sorted(filtered_df['report_date'].unique(), reverse=True)
    
    if len(unique_dates) == 0:
        st.warning("선택한 조건에 해당하는 결과가 없습니다.")
    else:
        # ---------------------------------------------------------
        # 날짜별 슬라이드 이동(화살표 네비게이션) 로직
        # ---------------------------------------------------------
        if 'date_index' not in st.session_state:
            st.session_state.date_index = 0
            
        # 선택된 타겟에 맞춰 전체 날짜 목록이 바뀌면 인덱스 보호(오류방지)
        if st.session_state.date_index >= len(unique_dates):
            st.session_state.date_index = 0
            
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            if st.button("⬅️ 이전 날짜 (과거)"):
                if st.session_state.date_index < len(unique_dates) - 1:
                    st.session_state.date_index += 1

        with col3:
            if st.button("다음 날짜 (최신) ➡️"):
                if st.session_state.date_index > 0:
                    st.session_state.date_index -= 1
                    
        # 화살표 버튼으로 결정된 현재 출력해야 할 날짜
        current_date_val = unique_dates[st.session_state.date_index]
        
        with col2:
            st.markdown(f"<h2 style='text-align: center; color: #4A90E2;'>📅 {current_date_val} 모닝 리포트</h2>", unsafe_allow_html=True)
            if selected_company != "전체 조회":
                st.markdown(f"<div style='text-align: center; font-size: 1.1rem; color: #E63946; font-weight: bold; background-color: #FDE8E9; padding: 8px; border-radius: 8px; margin-top: -10px;'>🎯 현재 [{selected_company}] 기업 타임라인만 모아보는 중입니다.</div>", unsafe_allow_html=True)
            
        st.divider()

        # ---------------------------------------------------------
        # 메인 리포트 렌더링 (현재 선택된 날짜 하루치만 보여줌)
        # ---------------------------------------------------------
        daily_df = filtered_df[filtered_df['report_date'] == current_date_val]
        st.subheader(f"📑 해당 일자의 타겟 리포트 총 {len(daily_df)}건")
        st.write("안구 피로 방지를 위해 화살표를 눌러 하루치 소식만 쾌적하게 봅니다.")
        
        for index, row in daily_df.iterrows():
            comp = row['competitor']
            # 한 화면에 하루치만 보이므로 모두 쫙 펼쳐줌!
            with st.expander(f"🏢 {comp} 인사이트 리포트", expanded=True):
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
