@echo off
chcp 65001 >nul
echo =======================================================
echo 🕵️ 시장/경쟁사 분석관 (Market Analyst) 자동화 세팅
echo =======================================================
echo.
echo 이 스크립트는 매일 데이터를 수집하고 매주 월요일에
echo 리포트를 발생하는 윈도우 스케줄러를 등록합니다.
echo.

set PYTHON_EXE=python
set BASE_DIR=%~dp0
set COLLECTOR_SCRIPT="%BASE_DIR%daily_collector.py"
set REPORTER_SCRIPT="%BASE_DIR%weekly_reporter.py"

echo [1/2] 매일 데이터 수집기 (매주 화~일 오전 8시 실행) 등록 중...
schtasks /create /tn "Deepfusion_Market_Collector" /tr "%PYTHON_EXE% '%COLLECTOR_SCRIPT%'" /sc weekly /d TUE,WED,THU,FRI,SAT,SUN /st 08:00 /f

echo [2/2] 매주 월요일 리포트 생성기 (매주 월요일 오전 8시 30분 실행) 등록 중...
schtasks /create /tn "Deepfusion_Market_Reporter" /tr "%PYTHON_EXE% '%REPORTER_SCRIPT%'" /sc weekly /d MON /st 08:30 /f

echo.
echo ✅ 모든 작업 스케줄러 등록이 완료되었습니다!
echo 설정된 스케줄을 확인하려면 '작업 스케줄러(taskschd.msc)' 앱을 실행하세요.
pause
