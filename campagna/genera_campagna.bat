@echo off
setlocal
cd /d "%~dp0"

set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY (
    echo Python non trovato. Installalo da https://www.python.org/downloads/
    echo e spunta "Add Python to PATH" durante l'installazione.
    pause
    exit /b 1
)

if not exist campagna.json (
    %PY% render_campagna.py --nuovo
    echo.
    echo Ho creato campagna.json vuoto. Compilalo, salvalo e rilancia questo file.
    start "" notepad campagna.json
    pause
    exit /b 0
)

%PY% render_campagna.py
if errorlevel 1 (
    echo.
    echo Errore: controlla che campagna.json sia scritto correttamente.
    pause
    exit /b 1
)

start "" campagna.html
