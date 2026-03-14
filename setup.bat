@echo off
echo ============================================
echo   MediSuperBot — Setup Script
echo ============================================
echo.

echo [1/3] Creating conda environment (Python 3.11)...
call conda create -n medisuperbot python=3.11 -y

echo.
echo [2/3] Activating environment and installing packages...
call conda activate medisuperbot
pip install -r requirements.txt

echo.
echo [3/3] Done! To start the server run:
echo.
echo   conda activate medisuperbot
echo   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
