@echo off
REM Запуск приложения ship-map-maker 

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "scripts\main.py" %*
) else (
    python "scripts\main.py" %*
)
if errorlevel 1 pause