@echo off
REM Arranca backend (puerto 8000) y frontend (puerto 5173) y abre el navegador.
cd /d "%~dp0"
if not exist backend\.venv call instalar.bat auto
if not exist frontend\node_modules call instalar.bat auto
start "Backend - FastAPI" /D "%~dp0backend" cmd /k "call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"
start "Frontend - React" /D "%~dp0frontend" cmd /k "npm run dev"
echo Esperando a que arranque...
timeout /t 6 /nobreak >nul
start http://localhost:5173
