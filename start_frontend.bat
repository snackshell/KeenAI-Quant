@echo off
echo ========================================
echo Starting KeenAI-Quant Frontend
echo ========================================
echo.

cd frontend

echo Installing dependencies (if needed)...
call npm install

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo.

call npm run dev

pause
