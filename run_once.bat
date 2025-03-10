@echo off

set ROOT_DIR="F:\UnrealProjects"
set FOLDER_NAME="Unreal Projects"

setlocal
set SCRIPT_DIR=%~dp0

if not exist "%SCRIPT_DIR%.venv\" (
    echo Creating virtual environment...
    python -m venv "%SCRIPT_DIR%.venv"
    echo Installing dependencies...
    call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
    pip install --upgrade -r "%SCRIPT_DIR%requirements.txt"
    deactivate
)

"%SCRIPT_DIR%.venv\Scripts\python.exe" "%SCRIPT_DIR%uproject-autoshortcut.py" --root %ROOT_DIR% --folder %FOLDER_NAME%
endlocal