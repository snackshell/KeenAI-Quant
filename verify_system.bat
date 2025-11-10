@echo off
echo ========================================
echo KeenAI-Quant System Verification
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running comprehensive system check...
echo.

python test_mt5_integration.py

echo.
echo ========================================
echo Verification Complete
echo ========================================
echo.
echo If all tests passed, you're ready to start!
echo Run: START_SYSTEM.bat
echo.
pause
