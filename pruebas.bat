@echo off
REM Corre las pruebas automaticas del backend.
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
python -m pytest -v
pause
