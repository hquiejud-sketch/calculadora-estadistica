@echo off
REM Crea el repositorio en GitHub y sube el proyecto (solo la primera vez).
cd /d "%~dp0"
set "GH=gh"
where gh >nul 2>nul
if not errorlevel 1 goto login
echo === Instalando GitHub CLI (si Windows pregunta, dale Si) ===
winget install --id GitHub.cli -e --silent --accept-source-agreements --accept-package-agreements
set "GH=C:\Program Files\GitHub CLI\gh.exe"

:login
"%GH%" auth status >nul 2>nul
if not errorlevel 1 goto subir
echo.
echo ================================================================
echo  El codigo de GitHub ya quedo COPIADO.
echo  1) Presiona ENTER aqui para abrir GitHub en tu navegador
echo  2) Pega el codigo (Ctrl+V), dale Continue y luego Authorize
echo ================================================================
"%GH%" auth login --hostname github.com --git-protocol https --web --clipboard
if errorlevel 1 goto error

:subir
"%GH%" auth setup-git
for /f "delims=" %%u in ('"%GH%" api user --jq .login') do set "GHUSER=%%u"
for /f "delims=" %%i in ('"%GH%" api user --jq .id') do set "GHID=%%i"
if not exist .git git init
git config user.name "%GHUSER%"
git config user.email "%GHID%+%GHUSER%@users.noreply.github.com"
git add .
git commit -m "Calculadora estadistica: FastAPI + React + SQLite + Gemini"
git branch -M main
git remote get-url origin >nul 2>nul
if not errorlevel 1 goto push
"%GH%" repo create calculadora-estadistica --public --source . --remote origin --description "Calculadora de estadistica descriptiva con tutor IA (FastAPI, React, SQLite, Gemini)"
if errorlevel 1 git remote add origin https://github.com/%GHUSER%/calculadora-estadistica.git

:push
git push -u origin main
if errorlevel 1 goto error
echo.
echo ===== LISTO: https://github.com/%GHUSER%/calculadora-estadistica =====
start "" https://github.com/%GHUSER%/calculadora-estadistica
pause
exit /b 0

:error
echo.
echo [ERROR] Algo fallo. Toma captura de esta ventana y mandasela a Claude.
pause
exit /b 1
