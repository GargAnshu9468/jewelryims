@echo off

REM Check if virtual environment folder exists
if not exist "ims_env\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv ims_env
)

REM Activate virtual environment
call ims_env\Scripts\activate.bat

REM Upgrade pip to latest
python -m pip install --upgrade pip >nul 2>&1

REM Install packages
python -m pip install -r requirements.txt >nul 2>&1

REM Run migrations silently
python manage.py makemigrations >nul 2>&1
python manage.py migrate >nul 2>&1

REM Start server in a new window so the batch file can continue
start "" python manage.py runserver 127.0.0.1:8000

REM Wait a few seconds to let the server start
timeout /t 5 /nobreak >nul

REM Open browser automatically
start "" "http://127.0.0.1:8000"
