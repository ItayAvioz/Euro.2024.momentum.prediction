@echo off
echo ========================================
echo Euro 2024 ARIMAX Dashboard
echo Period-Separated Momentum Version
echo ========================================
echo.
echo Starting Streamlit dashboard...
echo.

cd /d "%~dp0"
streamlit run main.py

pause

