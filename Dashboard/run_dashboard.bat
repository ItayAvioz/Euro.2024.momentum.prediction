@echo off
echo ======================================
echo    Euro 2024 Momentum Analytics
echo ======================================
echo.
echo Starting dashboard...
echo.
echo Dashboard will be available at:
echo http://localhost:8505
echo.
echo Press Ctrl+C to stop the dashboard
echo ======================================
echo.
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Starting Streamlit...
streamlit run main.py --server.port 8505 --server.headless false
echo.
echo Dashboard stopped.
pause
