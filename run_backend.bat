@echo off
cd /d "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
)
set PYTHONPATH=%CD%
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
