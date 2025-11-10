@echo off
echo ========================================
echo KeenAI-Quant Trading System
echo ========================================
echo.
echo This will start both backend and frontend
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to start...
pause > nul

REM Start backend in new window
start "KeenAI Backend" cmd /k "call venv\Scripts\activate.bat && python backend/main.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "KeenAI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo System Started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two windows opened:
echo 1. Backend Server (Python/FastAPI)
echo 2. Frontend Server (Next.js)
echo.
echo Close those windows to stop the system
echo.
pause
