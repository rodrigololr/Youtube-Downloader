# 📥 YouTube Downloader - PWA

Um aplicativo web simples e minimalista para baixar vídeos do YouTube. Funciona como PWA (Progressive Web App), permitindo instalar na área de trabalho!

## ✨ Características

- ✅ Interface extremamente simples e intuitiva
- ✅ Funciona offline (após primeira utilização)
- ✅ Instalável como app na área de trabalho
- ✅ Exibe qualidades disponíveis do vídeo
- ✅ Mostra tamanho aproximado de cada qualidade
- ✅ Backend com FastAPI
- ✅ Licença MIT
- ✅ Código simples e fácil de entender

## 🚀 Como Usar Localmente

### 1. Pré-requisitos
- Python 3.8+
- Git

### 2. Clonar o Repositório
```bash
git clone https://github.com/rodrigololr/Youtube-Downloader.git
cd Youtube-Downloader
```

### 3. Criar Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependências
```bash
pip install -r backend/requirements.txt
```

### 5. Rodar o Backend
```bash
cd backend
python main.py
```

O servidor estará rodando em `http://localhost:8000`

### 6. Abrir o Frontend
Abra seu navegador e acesse:
```
http://localhost:8000/static/index.html
```

Ou se preferir servir estático de outra forma:
```bash
# Na pasta frontend, use um servidor simples
cd frontend
python -m http.server 8001
# Acesse: http://localhost:8001
```

## 📱 Instalar como PWA

### No Chrome/Edge (Windows/Mac/Linux):
1. Abra a aplicação no navegador
2. Clique nos 3 pontos (⋮) no canto superior direito
3. Clique em "Instalar app" ou "Install app"
4. Pronto! O app aparecerá na sua área de trabalho

### No Safari (Mac):
1. Abra a aplicação no navegador
2. Clique em "Compartilhar"
3. Selecione "Adicionar à Tela Inicial"

## 🌍 Opções de Deploy Online

### Option 1: **Heroku** (Fácil, Gratuito até certo ponto)
```bash
# Criar Procfile na raiz
echo "web: cd backend && uvicorn main:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Deploy
git push heroku main
```

### Option 2: **Vercel** (Recomendado para Frontend)
```bash
# Só deploy do frontend estático (frontend/)
# Conectar repositório GitHub e fazer deploy automático
```

### Option 3: **PythonAnywhere** (Para Backend Python)
- Acesse: https://www.pythonanywhere.com
- Fazer upload dos arquivos
- Configurar app WSGI

### Option 4: **Railway** (Simples e Rápido)
- Conectar GitHub
- Selecionar o repositório
- Railway detecta automaticamente Python/FastAPI
- Deploy automático

### Option 5: **Replit** (Gratuito e Fácil)
- Acesse: https://replit.com
- Importar do GitHub
- Run automático

### Option 6: **VPS (DigitalOcean, Linode, AWS)**
```bash
# SSH na sua VPS
ssh root@seu_ip

# Clonar repositório
git clone https://github.com/rodrigololr/Youtube-Downloader.git

# Instalar Python
apt-get install python3-pip python3-venv

# Setup no servidor
cd Youtube-Downloader
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Usar Gunicorn + Nginx para produção
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app

# Configurar Nginx como reverse proxy
# ... (documentação mais detalhada em outros recursos)
```

## 📁 Estrutura do Projeto

```
Youtube-Downloader/
├── backend/
│   ├── main.py              # Servidor FastAPI
│   └── requirements.txt      # Dependências Python
├── frontend/
│   ├── index.html          # Interface principal
│   ├── style.css           # Estilos
│   ├── manifest.json       # Configuração PWA
│   └── sw.js              # Service Worker
├── venv/                    # Virtual environment (ignorado no git)
└── LICENSE                 # MIT License
```

## ⚙️ Configuração Avançada

### Mudar Porta do Backend
Editar `backend/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)  # Mudar 8000 para 3000
```

### Adicionar Senha/Autenticação
Seria necessário adicionar autenticação ao `main.py` usando `python-jose`, `passlib`, etc.

### Aumentar Limite de Tamanho
Ajustar configurações do `yt-dlp` em `backend/main.py`

## 🐛 Troubleshooting

### "Erro ao conectar com o servidor"
- Certifique-se que o backend está rodando em `http://localhost:8000`
- Verifique se a porta 8000 está disponível

### "Vídeo não encontrado"
- Verifique se o link do YouTube está correto
- Algumas regiões podem ter restrições
- Tente em modo incógnito

### "Arquivo não consegue ser instalado"
- Certifique-se de acessar via HTTPS em produção (PWA requer HTTPS)
- Localmente, HTTP funciona normalmente

## 📝 Licença

MIT License - Veja `LICENSE` para detalhes

## 🤝 Contribuições

Sinta-se à vontade para fazer fork, reportar bugs ou sugerir melhorias!

---

**Desenvolvido com ❤️ de forma simples e eficiente**
