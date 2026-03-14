@echo off
echo Starting MediSuperBot API...
call conda activate medisuperbot
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
