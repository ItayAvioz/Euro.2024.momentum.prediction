@echo off
echo Starting LLM vs Real Commentary Dashboard...
echo.
cd /d "%~dp0"
streamlit run app.py
pause

