#!/bin/bash

echo "========================================"
echo "YouTube Downloader - Setup Automático"
echo "========================================"
echo ""

echo "[1/4] Criando Virtual Environment..."
python3 -m venv venv
echo "OK!"

echo ""
echo "[2/4] Ativando Virtual Environment..."
source venv/bin/activate
echo "OK!"

echo ""
echo "[3/4] Instalando dependências..."
pip install -r backend/requirements.txt
echo "OK!"

echo ""
echo "========================================"
echo "Setup Completo!"
echo ""
echo "Para iniciar o servidor:"
echo "  1. Execute: source venv/bin/activate"
echo "  2. Execute: cd backend"
echo "  3. Execute: python main.py"
echo ""
echo "Depois acesse: http://localhost:8000/static/index.html"
echo "========================================"
