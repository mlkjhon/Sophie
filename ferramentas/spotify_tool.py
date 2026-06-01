"""
spotify_tool.py — Permite controlar o Spotify no Windows usando comandos nativos e ctypes para simular botões de mídia.
"""
import subprocess
import ctypes
import urllib.parse
import time

# Códigos de teclas de mídia no Windows (Virtual-Key Codes)
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

def simular_tecla_midia(vk_code):
    """Simula o aperto de uma tecla multimídia no teclado do Windows."""
    # Aperta a tecla
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    # Solta a tecla
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)

def controlar_spotify(acao: str, busca: str = "") -> str:
    """
    Controla o aplicativo do Spotify do usuário.
    'acao' deve ser: 'tocar', 'pausar', 'proxima', 'anterior', 'pesquisar'.
    'busca' só é usado se acao for 'pesquisar', com o nome da música/artista.
    """
    print(f"🎵 [Spotify] Executando ação: {acao} | Busca: {busca}")
    
    acao = acao.lower().strip()
    
    try:
        if acao in ["tocar", "pausar"]:
            simular_tecla_midia(VK_MEDIA_PLAY_PAUSE)
            return "✅ Comando de Tocar/Pausar enviado ao Spotify."
            
        elif acao == "proxima":
            simular_tecla_midia(VK_MEDIA_NEXT_TRACK)
            return "✅ Comando de Pular Música enviado ao Spotify."
            
        elif acao == "anterior":
            simular_tecla_midia(VK_MEDIA_PREV_TRACK)
            return "✅ Comando de Voltar Música enviado ao Spotify."
            
        elif acao == "pesquisar":
            if not busca:
                return "❌ Erro: Nenhuma música ou artista foi fornecido para a pesquisa."
                
            # Codifica a busca para URL (ex: "Linkin Park" vira "Linkin%20Park")
            busca_url = urllib.parse.quote(busca)
            
            # Usa o protocolo nativo do Spotify para abrir a pesquisa no app
            comando = f'start spotify:search:{busca_url}'
            subprocess.run(comando, shell=True)
            
            # Aguarda um segundinho para o app abrir
            time.sleep(2)
            
            # Toca a musica usando a tecla play
            # OBS: O Spotify não dá play automático na pesquisa nativa, então simulamos um 'enter' e 'play' 
            # ou deixamos para o usuário clicar. Mas tentar um play pode ajudar.
            simular_tecla_midia(VK_MEDIA_PLAY_PAUSE)
            
            return f"✅ Pesquisa por '{busca}' aberta no Spotify."
            
        else:
            return "❌ Ação desconhecida. Use 'tocar', 'pausar', 'proxima', 'anterior' ou 'pesquisar'."
            
    except Exception as e:
        return f"❌ Erro ao tentar controlar o Spotify: {e}"
