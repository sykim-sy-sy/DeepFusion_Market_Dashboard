import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# 프로젝트 루트 경로 추가 (Agents 모듈 임포트용)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from Agents import agent6_kakao_manager
except ImportError:
    pass

# 페이지 기본 설정
st.set_page_config(page_title="DeepFusion AI 마켓 대시보드", page_icon="DeepFusion", layout="wide")

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
    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 15px;
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .report-table th {
        background-color: #F8FAFC;
        color: #1A202C;
        font-weight: 700;
        padding: 16px;
        width: 15%;
        text-align: left;
        border-bottom: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
    }
    .report-table td {
        padding: 16px;
        color: #2D3748;
        line-height: 1.6;
        border-bottom: 1px solid #E2E8F0;
    }
    .report-table tr:last-child th, .report-table tr:last-child td {
        border-bottom: none;
    }
    .report-table a {
        color: #3182CE;
        text-decoration: none;
        font-weight: bold;
    }
    .report-table a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header"><span style="color:#004b87;">■</span> DeepFusion AI 모닝 인사이트 데스크</p>', unsafe_allow_html=True)

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

# 데이터 고유 경로 설정
LOGO_PATH = os.path.join(os.path.dirname(__file__), "deepfusion_logo.png")

# ---------------------------------------------------------
# 왼쪽 사이드바 (필터) 및 로고
# ---------------------------------------------------------
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.title("DeepFusion AI")

df = load_data()

# 메인 탭 구성
tab1, tab2 = st.tabs(["📊 마켓 뉴스 리포트", "📱 메신저 대화 분석"])

with tab1:
    if df.empty:
        st.info(" 아직 수집된 데이터가 없습니다. Lina의 자동화 에이전트가 실행되면 여기에 분석 데이터가 차곡차곡 쌓이게 됩니다.")
    else:
    st.sidebar.header(" 데이터 필터 탐색기")
    st.sidebar.write("보고 싶은 조건만 골라서 필터링하세요.")
    
    companies = ["전체 조회"] + list(df['competitor'].unique())
    selected_company = st.sidebar.selectbox(" 특정 경쟁사 집중 보기", companies)
    
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
            if st.button("◀ 이전 날짜"):
                if st.session_state.date_index < len(unique_dates) - 1:
                    st.session_state.date_index += 1

        with col3:
            if st.button("다음 날짜 ▶"):
                if st.session_state.date_index > 0:
                    st.session_state.date_index -= 1
                    
        # 화살표 버튼으로 결정된 현재 출력해야 할 날짜
        current_date_val = unique_dates[st.session_state.date_index]
        
        with col2:
            st.markdown(f"<h2 style='text-align: center; color: #4A90E2;'>■ {current_date_val} 모닝 리포트</h2>", unsafe_allow_html=True)
            if selected_company != "전체 조회":
                st.markdown(
                    f"<div style='text-align: center; font-size: 1.1rem; color: #2E7D32; font-weight: bold; background-color: #E8F5E9; padding: 6px; border-radius: 8px; margin-top: -10px; width: fit-content; margin-left: auto; margin-right: auto;'>"
                    f"<span style='color: #1B5E20;'>▪</span> {selected_company}"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            
        st.divider()

        # ---------------------------------------------------------
        # 메인 리포트 렌더링 (현재 선택된 날짜 하루치만 보여줌)
        # ---------------------------------------------------------
        daily_df = filtered_df[filtered_df['report_date'] == current_date_val].copy()
        
        # '■ 시장 및 기술 동향'이 있으면 리스트 최상단으로 정렬
        if 'competitor' in daily_df.columns:
            daily_df['is_trend'] = daily_df['competitor'].apply(lambda x: 1 if '시장 및 기술 동향' in str(x) else 0)
            daily_df = daily_df.sort_values(by='is_trend', ascending=False)
            
        st.subheader(f"■ 해당 일자의 타겟 리포트 총 {len(daily_df)}건")
        st.write(f"최신 데이터 업데이트 확인 완료 (기준일: {current_date_val})")
        
        for index, row in daily_df.iterrows():
            comp = row['competitor']
            # 한 화면에 하루치만 보이므로 모두 쫙 펼쳐줌!
            with st.expander(f"▪ {comp} 인사이트 리포트", expanded=True):
                # 텍스트 내 줄바꿈을 HTML <br>로 변환, 마크다운 총알(- ) 스타일링 적용
                facts_html = str(row["facts"]).replace('\n', '<br>').replace('- ', '• ')
                impl_html = str(row["implications"]).replace('\n', '<br>').replace('- ', '• ')
                
                urls_html = ""
                if row['urls'] and str(row['urls']).strip():
                    url_list = str(row['urls']).split('\n')
                    links = []
                    for i, u in enumerate(url_list):
                        u = u.strip()
                        if u:
                            links.append(f"<a href='{u}' target='_blank'>[링크 {i+1}]</a>")
                    urls_html = "&nbsp;&nbsp;|&nbsp;&nbsp;".join(links) if links else "없음"
                else:
                    urls_html = "<span style='color: #A0AEC0;'>제공된 링크가 없습니다.</span>"
                    
                table_html = f"""
                <table class="report-table">
                    <tr>
                        <th><span style='display:inline-block; width:4px; height:14px; background-color:#3182CE; vertical-align:middle; margin-right:8px;'></span>팩트 체크</th>
                        <td>{facts_html}</td>
                    </tr>
                    <tr>
                        <th><span style='display:inline-block; width:4px; height:14px; background-color:#D69E2E; vertical-align:middle; margin-right:8px;'></span>시사점</th>
                        <td>{impl_html}</td>
                    </tr>
                    <tr>
                        <th><span style='display:inline-block; width:4px; height:14px; background-color:#805AD5; vertical-align:middle; margin-right:8px;'></span>원문 출처</th>
                        <td>{urls_html}</td>
                    </tr>
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📱 카카오톡 대화 분석 (Lina V3.0)")
    st.write("카카오톡에서 내보낸 대화 내역(.txt)을 업로드하면 핵심 요약과 할 일을 정리해 드립니다.")
    
    uploaded_file = st.file_uploader("카카오톡 대화방 텍스트 파일 업로드", type=["txt"])
    
    if uploaded_file is not None:
        with st.status("Lina가 대화 내용을 분석 중입니다...", expanded=True) as status:
            content = uploaded_file.getvalue().decode("utf-8")
            st.write("데이터 파싱 중...")
            result = agent6_kakao_manager.analyze_chat(content)
            status.update(label="분석 완료!", state="complete", expanded=False)
        
        if "error" in result:
            st.error(result["error"])
        else:
            # 결과 렌더링
            st.success("✅ 대화 분석이 완료되었습니다.")
            
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown("#### 📝 대화 요약")
                st.info(result.get("summary", "요약 내용 없음"))
                
                st.markdown("#### 🎯 주요 결정 사항")
                decisions = result.get("decisions", [])
                if decisions:
                    for d in decisions:
                        st.write(f"- {d}")
                else:
                    st.write("감지된 결정 사항이 없습니다.")
            
            with c2:
                st.markdown("#### ✅ 할 일(To-Do)")
                todos = result.get("todos", [])
                if todos:
                    for t in todos:
                        with st.container(border=True):
                            st.write(f"**업무:** {t.get('task')}")
                            st.write(f"**담당:** {t.get('owner', '미정')}")
                            st.write(f"**기한:** {t.get('due', '미정')}")
                else:
                    st.write("추출된 할 일이 없습니다.")
