from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import json
from pathlib import Path

app = FastAPI()

# CORS - permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pasta para downloads
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
def read_root():
    return {"mensagem": "YouTube Downloader API rodando!"}


@app.get("/api/video-info")
def get_video_info(url: str):
    """Pega informações do vídeo (título, durações, qualidades)"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extrair informações importantes
            titulo = info.get('title', 'Vídeo')
            duracao = info.get('duration', 0)

            # Pegar formatos disponíveis (qualidades)
            formatos = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    altura = fmt.get('height', 0)
                    fps = fmt.get('fps', 30)

                    if altura and altura not in [f['altura'] for f in formatos]:
                        formatos.append({
                            'altura': altura,
                            'descricao': f"{altura}p",
                            'tamanho_aprox': calcular_tamanho(duracao, altura),
                            'format_id': fmt.get('format_id')
                        })

            # Ordenar qualidades de menor para maior
            formatos = sorted(formatos, key=lambda x: x['altura'])

            return {
                'titulo': titulo,
                'duracao': duracao,
                'qualidades': formatos
            }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao processar vídeo: {str(e)}")


@app.get("/api/download")
def download_video(url: str, qualidade: str = "best"):
    """Faz download do vídeo na qualidade especificada"""
    try:
        ydl_opts = {
            'format': qualidade,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            arquivo = ydl.prepare_filename(info)

            return {
                'sucesso': True,
                'arquivo': os.path.basename(arquivo),
                'caminho': arquivo
            }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro no download: {str(e)}")


def calcular_tamanho(duracao, altura):
    """Calcula tamanho aproximado do vídeo em MB"""
    # Aproximação: ~0.5MB por minuto em 720p, varia com qualidade
    minutos = duracao / 60

    # Multiplicador por qualidade
    if altura <= 360:
        tamanho = minutos * 0.3  # ~18MB por 10 min em 360p
    elif altura <= 480:
        tamanho = minutos * 0.5  # ~30MB por 10 min em 480p
    elif altura <= 720:
        tamanho = minutos * 1.0  # ~60MB por 10 min em 720p
    elif altura <= 1080:
        tamanho = minutos * 2.0  # ~120MB por 10 min em 1080p
    else:
        tamanho = minutos * 3.0  # ~180MB por 10 min em 2160p

    return round(tamanho, 1)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
