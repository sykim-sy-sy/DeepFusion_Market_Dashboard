import streamlit as st
import os
import sys

# 프로젝트 루트 경로 추가 (Agents 모듈 임포트용)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from Agents import agent6_kakao_manager

# 페이지 기본 설정
st.set_page_config(page_title="Lina 업무 보조 도구", page_icon="📱", layout="centered")

# CSS 스타일링 (Aesthetics)
st.markdown("""
    <style>
    .assistant-header {
        font-size: 2.2rem;
        color: #2D3748;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    .assistant-sub {
        font-size: 1rem;
        color: #718096;
        text-align: center;
        margin-bottom: 30px;
    }
    .summary-card {
        background-color: #EDF2F7;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #4A5568;
        margin-bottom: 20px;
    }
    .todo-card {
        background-color: #F7FAFC;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="assistant-header">📱 Lina 업무 보조 도구 (V3.0)</p>', unsafe_allow_html=True)
st.markdown('<p class="assistant-sub">카카오톡 대화방 내용을 분석하여 요약 및 할 일을 정리해 드립니다.</p>', unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.header("📁 데이터 업로드")
st.sidebar.write("카카오톡에서 내보낸 텍스트(.txt) 파일을 업로드하세요.")
uploaded_file = st.sidebar.file_uploader("파일 선택", type=["txt"])

if uploaded_file is not None:
    with st.status("Lina가 대화 내용을 분석 중입니다...", expanded=True) as status:
        content = uploaded_file.getvalue().decode("utf-8")
        st.write("메시지 데이터 파싱 중...")
        result = agent6_kakao_manager.analyze_chat(content)
        status.update(label="분석 완료!", state="complete", expanded=False)
    
    if "error" in result:
        st.error(result["error"])
    else:
        st.balloons()
        st.success("✅ 분석이 완료되었습니다.")
        
        # 메인 영역 출력
        st.markdown("### 📝 대화 요약")
        st.markdown(f"""
        <div class="summary-card">
            {result.get('summary', '요약 내용이 없습니다.')}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🎯 주요 결정 사항")
            decisions = result.get("decisions", [])
            if decisions:
                for d in decisions:
                    st.markdown(f"✅ {d}")
            else:
                st.write("감지된 결정 사항이 없습니다.")
                
        with col2:
            st.markdown("#### 🚀 할 일 (To-Do)")
            todos = result.get("todos", [])
            if todos:
                for t in todos:
                    with st.container(border=True):
                        st.markdown(f"**업무:** {t.get('task')}")
                        st.markdown(f"**담당:** `{t.get('owner', '미정')}`")
                        st.markdown(f"**기한:** {t.get('due', '미정')}")
            else:
                st.write("추출된 할 일이 없습니다.")

else:
    st.info("왼쪽 사이드바에서 카카오톡 대화 내역 파일을 업로드해 주세요.")
    
    with st.expander("❓ 사용법 안내"):
        st.write("""
        1. 카카오톡 대화방 진입
        2. 설정(톱니바퀴 또는 메뉴) > **대화 내용 내보내기**
        3. **텍스트만 저장** 선택 후 생성된 파일을 업로드
        """)
