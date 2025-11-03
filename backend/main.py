from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
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

# Obter caminho do frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
def read_root():
    """Serve o index.html do frontend"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"mensagem": "YouTube Downloader API rodando!"}


# Servir arquivos estáticos do frontend
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


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
                        qualidades_video.append({
                            'altura': altura,
                            'descricao': descrever_qualidade_video(altura),
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
def download_video(url: str, format_id: str = "best", tipo: str = "video"):
    """Faz streaming do vídeo ou áudio direto para o usuário
    
    tipo: "video" (vídeo + áudio) ou "audio" (só áudio)
    format_id: o format_id selecionado (vídeo ou áudio)
    """
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

                # Pegar URL de streaming do vídeo/áudio
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

        # Definir extensão e tipo de mídia
        if tipo == "audio":
            extensao = ".m4a"
            media_type = "audio/mp4"
        else:
            extensao = ".mp4"
            media_type = "video/mp4"

        titulo = obter_titulo_video(url)
        filename = f"{titulo}{extensao}"
        filename_safe = "".join(
            c for c in filename if c.isalnum() or c in (' ', '.', '-')).rstrip()

        return StreamingResponse(
            gerar(),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename_safe}"}
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro: {str(e)}")


def descrever_qualidade_video(altura):
    """Descreve a qualidade do vídeo com resolução e arquivo"""
    if altura <= 360:
        return f"{altura}p (qualidade do vídeo ruim, mas arquivo leve)"
    elif altura <= 480:
        return f"{altura}p (qualidade do vídeo ok, mas arquivo leve)"
    elif altura <= 720:
        return f"{altura}p (qualidade do vídeo boa e arquivo mediano)"
    elif altura <= 1080:
        return f"{altura}p (qualidade do vídeo bela e arquivo maior)"
    else:
        return f"{altura}p (qualidade 4K - arquivo muito grande)"


def descrever_qualidade_audio(bitrate):
    """Descreve a qualidade do áudio com bitrate e arquivo"""
    if bitrate < 96:
        return f"{int(bitrate)}kbps (áudio ruim, mas arquivo leve)"
    elif bitrate < 192:
        return f"{int(bitrate)}kbps (áudio ok, mas arquivo leve)"
    elif bitrate < 256:
        return f"{int(bitrate)}kbps (áudio bom e arquivo mediano)"
    else:
        return f"{int(bitrate)}kbps (áudio top - arquivo maior)"


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
