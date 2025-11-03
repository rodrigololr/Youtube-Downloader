@echo off
echo ========================================
echo YouTube Downloader - Setup Automatico
echo ========================================
echo.

echo [1/4] Criando Virtual Environment...
python -m venv venv
echo OK!

echo.
echo [2/4] Ativando Virtual Environment...
call venv\Scripts\activate.bat
echo OK!

echo.
echo [3/4] Instalando dependencias...
pip install -r backend\requirements.txt
echo OK!

echo.
echo ========================================
echo Setup Completo!
echo.
echo Para iniciar o servidor:
echo   1. Execute: venv\Scripts\activate.bat
echo   2. Execute: cd backend
echo   3. Execute: python main.py
echo.
echo Depois acesse: http://localhost:8000/static/index.html
echo ========================================
pause
