@echo off
set "PYTHON_EXE=python"
set "WORKING_DIR=c:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team"
cd /d "%WORKING_DIR%"

echo ==================================================
echo [Lina] 시장 분석 에이전트를 시작합니다...
echo 작성일: %date% %time%
echo ==================================================

"%PYTHON_EXE%" "%WORKING_DIR%\Agents\agent1_market_analyst.py"

if %errorlevel% neq 0 (
    echo.
    echo [오류] 에이전트 실행 중 문제가 발생했습니다. (Error Level: %errorlevel%)
    timeout /t 30
)

echo.
echo ==================================================
echo 실행이 완료되었습니다. 창은 10초 뒤에 자동으로 닫힙니다.
echo ==================================================
timeout /t 10
