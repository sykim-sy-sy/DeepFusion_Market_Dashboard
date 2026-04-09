@echo off
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
cd /d "%~dp0"
echo ==================================================
echo 리나의 아침 보고 시스템을 실행합니다...
echo ==================================================
"%PYTHON_EXE%" main.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 스크립트 실행 중 문제가 발생했습니다.
    pause
)
echo.
echo ==================================================
echo 실행이 완료되었습니다. 창은 10초 뒤에 자동으로 닫힙니다.
echo ==================================================
timeout /t 10
