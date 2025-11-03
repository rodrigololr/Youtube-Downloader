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

            # Pegar qualidades de VÍDEO (formatos com vcodec mas sem áudio)
            qualidades_video = {}  # usar dict para evitar duplicatas por altura
            for fmt in info.get('formats', []):
                # Procurar formatos de vídeo PURO (sem áudio integrado)
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                    altura = fmt.get('height', 0)
                    
                    # Só adicionar se temos altura e se é um formato válido
                    if altura and altura > 0:
                        # Se já existe uma qualidade com essa altura, pegar a com melhor qualidade
                        if altura not in qualidades_video or fmt.get('tbr', 0) > qualidades_video[altura]['tbr']:
                            qualidades_video[altura] = {
                                'altura': altura,
                                'descricao': descrever_qualidade_video(altura),
                                'format_id': fmt.get('format_id'),
                                'tbr': fmt.get('tbr', 0)
                            }
            
            # Converter de dict para lista e remover campo tbr temporário
            qualidades_video = [
                {'altura': v['altura'], 'descricao': v['descricao'], 'format_id': v['format_id']}
                for v in qualidades_video.values()
            ]

            # Pegar qualidades de ÁUDIO (formatos com acodec mas sem vídeo)
            qualidades_audio = {}  # usar dict para evitar duplicatas por bitrate
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    abr = fmt.get('abr', fmt.get('tbr', 128))
                    
                    if abr and abr > 0:
                        # Se não existe ou esse é melhor, adicionar
                        if abr not in qualidades_audio or fmt.get('tbr', 0) > qualidades_audio[abr]['tbr']:
                            qualidades_audio[abr] = {
                                'bitrate': abr,
                                'descricao': descrever_qualidade_audio(abr),
                                'format_id': fmt.get('format_id'),
                                'tbr': fmt.get('tbr', 0)
                            }
            
            # Converter de dict para lista e remover campo tbr temporário
            qualidades_audio = [
                {'bitrate': v['bitrate'], 'descricao': v['descricao'], 'format_id': v['format_id']}
                for v in qualidades_audio.values()
            ]

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
            if tipo == "video":
                # Para vídeo, precisa combinar com áudio: "formato_video+formato_audio"
                # Pegar o melhor áudio disponível
                ydl_opts_info = {
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 30,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Encontrar melhor áudio
                    best_audio = None
                    for fmt in info.get('formats', []):
                        if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                            if best_audio is None or fmt.get('abr', fmt.get('tbr', 0)) > best_audio.get('abr', best_audio.get('tbr', 0)):
                                best_audio = fmt
                    
                    if best_audio:
                        # Combinar formato_video + formato_audio
                        format_combined = f"{format_id}+{best_audio.get('format_id')}"
                    else:
                        format_combined = format_id
                
                ydl_opts = {
                    'format': format_combined,
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 30,
                }
            else:
                # Para áudio, usar o format_id direto
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
                    if fmt.get('format_id') == format_id or fmt.get('format_id') == f"{format_id}+{info.get('best_audio_format_id', '')}":
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
                            return
                
                # Se não encontrou direto, tentar com a lista de formatos disponível
                # yt-dlp já selecionou o melhor formato compatível
                if 'url' in info:
                    stream_url = info.get('url')
                    if stream_url:
                        import urllib.request
                        with urllib.request.urlopen(stream_url) as response:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                yield chunk

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
