@echo off

REM Create virtual environment if not already
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip to latest
python -m pip install --upgrade pip >nul 2>&1

REM Pull latest changes from GitHub
echo Checking for an update...
git pull

REM Install project requirements
python -m pip install -r requirements.txt >nul 2>&1

REM Make & run migrations silently
python manage.py makemigrations >nul 2>&1
python manage.py migrate >nul 2>&1

REM Start server in a new window
start "" python manage.py runserver 127.0.0.1:8000

REM Wait a few seconds to let the server start
timeout /t 5 /nobreak >nul

REM Open browser automatically
start "" "http://127.0.0.1:8000"
