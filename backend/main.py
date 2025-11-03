from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import io

app = FastAPI()

# CORS - permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
def read_root():
    return {"mensagem": "YouTube Downloader API rodando!"}


@app.get("/api/video-info")
def get_video_info(url: str):
    """Pega informações do vídeo (título, duração, qualidades e áudio)"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            titulo = info.get('title', 'Vídeo')
            duracao = info.get('duration', 0)

            # Pegar qualidades de VÍDEO
            qualidades_video = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    altura = fmt.get('height', 0)

                    if altura and altura not in [f['altura'] for f in qualidades_video]:
                        descricao = descrever_qualidade_video(altura)
                        qualidades_video.append({
                            'altura': altura,
                            'descricao': descricao,
                            'format_id': fmt.get('format_id')
                        })

            # Pegar qualidades de ÁUDIO
            qualidades_audio = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    abr = fmt.get('abr', fmt.get('tbr', 128))

                    if abr and abr not in [f['bitrate'] for f in qualidades_audio]:
                        descricao = descrever_qualidade_audio(abr)
                        qualidades_audio.append({
                            'bitrate': abr,
                            'descricao': descricao,
                            'format_id': fmt.get('format_id')
                        })

            # Ordenar
            qualidades_video = sorted(
                qualidades_video, key=lambda x: x['altura'])
            qualidades_audio = sorted(
                qualidades_audio, key=lambda x: x['bitrate'], reverse=True)

            return {
                'titulo': titulo,
                'duracao': duracao,
                'qualidades_video': qualidades_video,
                'qualidades_audio': qualidades_audio
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro: {str(e)}")


@app.get("/api/download")
def download_video(url: str, format_id: str = "best"):
    """Faz streaming do vídeo direto para o usuário"""
    try:
        def gerar():
            ydl_opts = {
                'format': format_id,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Pegar URL de streaming do vídeo
                for fmt in info.get('formats', []):
                    if fmt.get('format_id') == format_id:
                        stream_url = fmt.get('url')
                        if stream_url:
                            # Fazer requisição ao stream
                            import urllib.request
                            with urllib.request.urlopen(stream_url) as response:
                                while True:
                                    chunk = response.read(8192)
                                    if not chunk:
                                        break
                                    yield chunk
                        break

        titulo = obter_titulo_video(url)
        filename = f"{titulo}.mp4"
        filename_safe = "".join(
            c for c in filename if c.isalnum() or c in (' ', '.', '-')).rstrip()

        return StreamingResponse(
            gerar(),
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={filename_safe}"}
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro: {str(e)}")


def descrever_qualidade_video(altura):
    """Descreve a qualidade do vídeo de forma simples"""
    if altura <= 360:
        return "Qualidade ruim, mas leve"
    elif altura <= 480:
        return "Qualidade ok, mas leve"
    elif altura <= 720:
        return "Qualidade boa"
    elif altura <= 1080:
        return "Qualidade bela"
    else:
        return "Qualidade top (4K)"


def descrever_qualidade_audio(bitrate):
    """Descreve a qualidade do áudio de forma simples"""
    if bitrate < 96:
        return "Áudio ruim, mas leve"
    elif bitrate < 192:
        return "Áudio ok"
    elif bitrate < 256:
        return "Áudio bom"
    else:
        return "Áudio top"


def obter_titulo_video(url):
    """Pega o título do vídeo"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', 'video')
    except:
        return 'video'


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
