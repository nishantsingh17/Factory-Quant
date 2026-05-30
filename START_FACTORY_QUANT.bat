@echo off
:: This line forces the terminal to move to the folder where this .bat file lives
cd /d "%~dp0"

echo ===================================================
echo Starting Factory-Quant SMT Planner...
echo Please wait while we check for required libraries.
echo ===================================================

:: Install requirements quietly
pip install -r requirements.txt -q

:: Start the Streamlit app
echo Launching dashboard in your browser...
python -m streamlit run app.py

pause
