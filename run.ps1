Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " MultiFactor 인터랙티브 플레이그라운드 실행 중..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" -m streamlit run app.py
