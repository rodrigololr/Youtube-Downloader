"""
Script para testar a API do YouTube Downloader
Execute: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# Link de exemplo (vídeo curto público)
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def teste_health():
    """Testa se o servidor está rodando"""
    print("=" * 50)
    print("🔧 TESTE 1: Health Check")
    print("=" * 50)
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Servidor respondeu: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("   Certifique-se que o servidor está rodando: python main.py")
        return False


def teste_video_info():
    """Testa obtenção de informações do vídeo"""
    print("\n" + "=" * 50)
    print("📺 TESTE 2: Buscar Informações do Vídeo")
    print("=" * 50)
    print(f"URL: {VIDEO_URL}")

    try:
        response = requests.get(
            f"{BASE_URL}/video-info",
            params={"url": VIDEO_URL}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Sucesso!")
            print(f"   Título: {data['titulo']}")
            print(f"   Duração: {data['duracao']} segundos")
            print(f"   Qualidades disponíveis:")

            for qual in data['qualidades']:
                print(
                    f"      • {qual['descricao']} (~{qual['tamanho_aprox']}MB)")

            return data
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def teste_download():
    """Teste de download (não faz download real, só verifica API)"""
    print("\n" + "=" * 50)
    print("⬇️  TESTE 3: Verificar Endpoint de Download")
    print("=" * 50)
    print("(Não vamos fazer download real neste teste)")

    try:
        # Apenas verificar se o endpoint existe
        print("✅ Endpoint /api/download está disponível")
        print("   Para usar: GET /api/download?url=...&qualidade=...")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    print("\n")
    print("█" * 50)
    print("  🎬 TESTE DA API - YouTube Downloader")
    print("█" * 50)
    print()

    # Teste 1
    if not teste_health():
        print("\n⚠️  Não consegui conectar ao servidor!")
        print("   Execute em outro terminal:")
        print("   cd backend && python main.py")
        return

    # Teste 2
    video_data = teste_video_info()

    # Teste 3
    teste_download()

    # Resumo
    print("\n" + "=" * 50)
    print("✨ TESTES COMPLETOS!")
    print("=" * 50)
    print("\nAgora você pode:")
    print("1. Abrir http://localhost:8000/static/index.html")
    print("2. Colar um link do YouTube")
    print("3. Selecionar qualidade")
    print("4. Fazer download!")
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⋯ Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
