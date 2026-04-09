@echo off
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
echo ==================================================
echo 리나의 아침 보고 시스템 - 초기 설정을 시작합니다.
echo ==================================================
echo.
echo 1. Python이 설치되어 있는지 확인합니다...
"%PYTHON_EXE%" --version
if %errorlevel% neq 0 (
    echo [경고] Python 경로를 찾을 수 없습니다! 설치가 정상적으로 되지 않았습니다.
    pause
    exit /b
)

echo.
echo 2. 필요한 라이브러리를 설치합니다...
"%PYTHON_EXE%" -m pip install -r requirements.txt

echo.
echo ==================================================
echo 초기 설정이 완료되었습니다!
echo '.env' 파일 안의 내용을 모두 채워주셨다면 'run.bat'를 실행하여 테스트 해보세요.
echo ==================================================
pause
