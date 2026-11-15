@echo off
chcp 65001 > nul
echo ========================================================
echo  MultiFactor 인터랙티브 플레이그라운드 실행 중...
echo ========================================================
".venv\Scripts\python.exe" -m streamlit run app.py
pause
