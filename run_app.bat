@echo off
cd /d "%~dp0"
call .venv\Scripts\activate 2>nul
echo Starting Referral Engine...
start "" http://localhost:8501
streamlit run app\ui\dashboard.py --server.port 8501 --browser.gatherUsageStats false
pause
