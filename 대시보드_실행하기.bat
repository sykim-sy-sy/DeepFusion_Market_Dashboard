@echo off
chcp 65001 > nul
title DeepFusion AI 마켓 대시보드 런칭 컨트롤러

echo ==================================================
echo   📊 DeepFusion AI 모닝 인사이트 데스크 실행 중...
echo ==================================================
echo.
echo 로컬 데이터베이스와 분석 엔진을 불러오고 있습니다.
echo 잠시만 기다리시면 웹 브라우저 창이 자동으로 열립니다!
echo.
echo (종료하려면 이 까만색 창을 닫아주세요)
echo ==================================================

cd /d "%~dp0\Market_Analyst_Data"
python -m streamlit run dashboard_app.py

pause
