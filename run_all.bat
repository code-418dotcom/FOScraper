@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Always run from this script's folder
cd /d "%~dp0"

REM 1) Ensure venv exists
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    py -m venv .venv || goto :err
)

REM 2) Activate venv
call .venv\Scripts\activate.bat || goto :err

REM 3) Install requirements
pip install -r requirements.txt
playwright install

REM 4) Run combined scraper
python combined_scraper.py --pages 104 --outfile freeones_all_104.csv --delay 1 --concurrency 3

echo [OK] Done.
pause
exit /b 0

:err
echo [ERROR] Failed to run.
pause
exit /b 1
