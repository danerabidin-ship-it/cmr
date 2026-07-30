@echo off
cd /d "%~dp0"

cd frontend
call npm install
call npm run build
cd ..

cd backend
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
python main.py
