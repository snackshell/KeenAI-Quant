@echo off
echo ========================================
echo Starting KeenAI-Quant Backend
echo ========================================
echo.

REM Activate virtual environment and start backend
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo.

python backend/main.py

pause
