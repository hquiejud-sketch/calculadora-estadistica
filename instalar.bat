@echo off
REM Instala todo lo necesario (solo la primera vez).
cd /d "%~dp0"
echo.
echo ===== 1/2 Backend (Python) =====
cd backend
if not exist .venv (
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No encontre Python. Instala Python y marca "Add python.exe to PATH".
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env >nul
cd ..
echo.
echo ===== 2/2 Frontend (Node) =====
cd frontend
call npm install
if errorlevel 1 (
  echo [ERROR] Fallo npm. Revisa que Node.js este instalado.
  pause
  exit /b 1
)
cd ..
echo.
echo ===== Listo. Ahora abre iniciar.bat =====
if not "%1"=="auto" pause
