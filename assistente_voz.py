"""
assistente_voz.py — Assistente de voz da Sophie (Edge TTS + pyttsx3 fallback)
- STT: Google Speech Recognition (pt-BR + en-US fallback)
- TTS: Edge TTS (Microsoft) — pt-BR-FranciscaNeural (feminina, natural, expressiva)
         Fallback automático para pyttsx3 offline
- API: Railway (https://sophie-production.up.railway.app/chat)
- YouTube / Spotify: interceptadores de comando diretos
"""

import speech_recognition as sr
import requests
import os
import time
import sys
import re
import webbrowser
import urllib.parse
import threading
import subprocess
import tempfile
import asyncio
import edge_tts
import pyttsx3

# Importa o módulo do backend do YouTube
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend_youtube'))
from mecanismo_busca import buscar_videos_no_youtube, disparar_abertura_do_video

# ─── Configurações Edge TTS ───
EDGE_TTS_VOICE = "pt-BR-FranciscaNeural"  # Feminina, natural, expressiva (cheerful, friendly, sad, angry, etc.)
EDGE_TTS_STYLE = "cheerful"                # Estilo: cheerful, friendly, sad, angry, excited, terrified, shouting, whispering

# URL da API (pode ser sobrescrita por variável de ambiente)
API_URL = os.getenv("SOPHIE_API_URL", "https://sophie-production.up.railway.app/chat")


# ─── pyttsx3 Fallback (offline) ───
tts_engine = None
def init_pyttsx3():
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 165)
        tts_engine.setProperty('volume', 1.0)
        # Seleciona voz feminina PT-BR
        voz_selecionada = None
        for voice in tts_engine.getProperty('voices'):
            nome = voice.name.lower()
            if any(k in nome for k in ('maria', 'helena', 'camila', 'isabela', 'fernanda', 'patricia', 'lucia', 'ana')):
                if any(k in nome for k in ('portuguese', 'brazil', 'pt-br', 'pt_br', 'brasil')):
                    voz_selecionada = voice.id
                    break
        if voz_selecionada is None:
            for voice in tts_engine.getProperty('voices'):
                if any(k in voice.name.lower() for k in ('portuguese', 'brazil', 'pt-br', 'pt_br', 'brasil')):
                    voz_selecionada = voice.id
                    break
        if voz_selecionada is None:
            for voice in tts_engine.getProperty('voices'):
                if any(k in voice.name.lower() for k in ('female', 'woman', 'girl', 'feminina', 'mulher')):
                    voz_selecionada = voice.id
                    break
        if voz_selecionada:
            tts_engine.setProperty('voice', voz_selecionada)
            print(f"[pyttsx3] Voz: {voz_selecionada}")
    return tts_engine


# ─── Utilitários ───
class Spinner:
    def __init__(self):
        self.chars = ['|', '/', '-', '\\']
        self.running = False
        self.thread = None

    def _spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f'\r{self.chars[i % 4]} ')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write('\r   \r')
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)


def falar_edge_tts(texto: str, style: str = None) -> bool:
    """Fala via Edge TTS (Microsoft). Retorna True se sucesso, False se falhar."""
    try:
        voice = EDGE_TTS_VOICE
        use_style = style or EDGE_TTS_STYLE

        # Edge TTS 7.x não tem parâmetro style direto - usa SSML com mstts:express-as
        # Constrói SSML para estilo expressivo
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="pt-BR">
    <voice name="{voice}">
        <mstts:express-as style="{use_style}">
            {texto}
        </mstts:express-as>
    </voice>
</speak>'''

        communicate = edge_tts.Communicate(ssml, voice)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        # Executa async save
        asyncio.run(communicate.save(temp_path))

        # Toca o áudio
        try:
            if sys.platform == "win32":
                os.startfile(temp_path)
            elif sys.platform == "darwin":
                subprocess.run(["afplay", temp_path], check=False)
            else:
                subprocess.run(["aplay", temp_path], check=False)
        except Exception as e:
            print(f"[Edge TTS] Erro ao tocar: {e}")
            return False
        finally:
            # Remove após tocar (dá tempo)
            threading.Timer(5.0, lambda: os.path.exists(temp_path) and os.unlink(temp_path)).start()

        return True

    except Exception as e:
        print(f"[Edge TTS] Exceção: {e}")
        return False


def falar_pyttsx3(texto: str):
    """Fala via pyttsx3 (offline, sempre funciona)."""
    try:
        engine = init_pyttsx3()
        print(f"Sophie: {texto}")
        if not texto.strip():
            return
        engine.say(texto)
        engine.runAndWait()
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"[pyttsx3] Erro: {e}")


def falar(texto: str):
    """Fala com Edge TTS (primário); se falhar, cai para pyttsx3."""
    if not texto.strip():
        return
    print(f"Sophie: {texto}")
    # Tenta Edge TTS primeiro (grátis, sem chave, neural, expressivo)
    if falar_edge_tts(texto):
        return
    # Fallback silencioso
    print("[TTS] Edge TTS falhou, usando pyttsx3 offline...")
    falar_pyttsx3(texto)


def escutar_microfone() -> str | None:
    """Ouve o microfone e retorna o texto reconhecido (ou None)."""
    r = sr.Recognizer()

    r.energy_threshold = 200
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1.0
    r.phrase_threshold = 0.3

    with sr.Microphone() as source:
        print("\nAjustando ruido ambiente...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Ouvindo... (fale agora)")

        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=20)

            with Spinner():
                try:
                    texto = r.recognize_google(audio, language='pt-BR').lower().strip()
                except sr.UnknownValueError:
                    texto = r.recognize_google(audio, language='en-US').lower().strip()

            correcoes = {
                "valente": "valorant", "valera": "valorant",
                "chati g p t": "chatgpt", "chat e g p t": "chatgpt",
                "espotifai": "spotify", "spoti": "spotify",
                "backe e ba": "backend", "back end": "backend", "beck end": "backend",
                "front end": "frontend", "fronte end": "frontend",
                "full stack": "fullstack", "ful steck": "fullstack",
                "de bug": "debug", "de bugar": "debugar",
                "banco de dados": "database", "da ta base": "database",
                "paiton": "python", "pai ton": "python", "pai tao": "python",
                "java script": "javascript", "javiscript": "javascript",
                "tai pes cript": "typescript", "type script": "typescript",
                "re act": "react", "riect": "react",
                "next d e s": "nextjs", "next js": "nextjs",
                "n d e s": "nodejs", "node js": "nodejs",
                "v o e": "vue", "v u e": "vue",
                "teio in de": "tailwindcss", "tailwind": "tailwindcss",
                "v i s code": "vscode", "vs code": "vscode", "v s code": "vscode",
                "git rub": "github", "git hub": "github",
                "do que r": "docker", "doquer": "docker",
                "ku ber netes": "kubernetes", "a p i": "api",
            }
            for errado, certo in correcoes.items():
                texto = texto.replace(errado, certo)

            print(f"Voce: {texto}")
            return texto

        except sr.WaitTimeoutError:
            print("Tempo esgotado - nenhum audio detectado")
            return None
        except sr.UnknownValueError:
            print("Nao entendi o que voce disse")
            return None
        except sr.RequestError as e:
            print(f"Erro STT (Google): {e}")
            return None


def chamar_api(texto: str) -> str:
    """Envia texto para a API e retorna a resposta."""
    try:
        with Spinner():
            resp = requests.post(API_URL, json={"texto": texto}, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("resposta", "Erro: resposta vazia")
        return f"Erro API ({resp.status_code}): {resp.text}"
    except requests.exceptions.ConnectionError:
        return "Nao consegui conectar na API. Verifique se o Railway esta online."
    except Exception as e:
        return f"Erro ao chamar API: {e}"


# ─── Interceptadores de comando direto ───
def handle_youtube(frase: str) -> bool:
    gatilhos = ['youtube', 'pesquisar vídeo', 'buscar vídeo', 'procura vídeo', 'abre youtube']
    if not any(g in frase for g in gatilhos):
        return False

    falar("Acessando o YouTube...")

    termo = frase
    for p in [r'\byoutube\b', r'\bpesquisar\b', r'\bbuscar\b', r'\bprocurar\b',
              r'\bvídeos?\b', r'\bsobre\b', r'\bpor\b', r'\bno\b', r'\bum\b',
              r'\bo\b', r'\ba\b', r'\babrir\b', r'\babra\b', r'\bquero\b',
              r'\bver\b', r'\bpesquise\b', r'\bde\b', r'\bdo\b', r'\bda\b']:
        termo = re.sub(p, '', termo, flags=re.IGNORECASE)
    termo = re.sub(r'\s+', ' ', termo).strip()

    if not termo:
        falar("Abrindo a página inicial do YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True

    falar(f"Buscando por {termo}.")
    resultado = buscar_videos_no_youtube(termo)

    if resultado and resultado["lista_videos"]:
        v = resultado["lista_videos"][0]
        falar(f"Encontrei: {v['titulo']} do canal {v['canal']}. Abrindo...")
        disparar_abertura_do_video(v['link'])
    else:
        falar("Não encontrei resultados para essa busca.")
    return True


def handle_spotify(frase: str) -> bool:
    import pyautogui

    gatilhos_acao = ['abra', 'abre', 'abrir', 'tocar', 'toque', 'ouvir',
                     'coloca', 'colocar', 'pesquisar', 'buscar', 'procura']
    gatilhos_media = ['toca ', 'toque ', 'tocar ', 'quero ouvir ', 'queria ouvir ',
                      'coloca ', 'pula ', 'pular ', 'próxima', 'proxima', 'passa', 'pausar', 'pause ', 'pare ']

    eh_spotify = ('spotify' in frase and any(g in frase for g in gatilhos_acao)) or \
                 any(g in frase for g in gatilhos_media) or \
                 ('música' in frase and any(v in frase for v in ['tocar', 'toca', 'ouvir', 'pausar', 'parar']))

    if not eh_spotify:
        return False

    if any(p in frase for p in ['pause', 'pausar', 'pare', 'parar', 'pausa']):
        falar("Pausando.")
        pyautogui.press('playpause')
        return True
    if any(p in frase for p in ['pular', 'pula', 'próxima', 'proxima', 'passar', 'passa', 'avançar']):
        falar("Pulando.")
        pyautogui.press('nexttrack')
        return True

    falar("Conectando ao Spotify...")

    termo = frase
    for p in [r'\bspotify\b', r'\bquero\b', r'\bqueria\b', r'\bouvir\b',
              r'\bcoloca\b', r'\btocar\b', r'\btoque\b', r'\btoca\b',
              r'\babrir\b', r'\babra\b', r'\babre\b', r'\bmúsica\b',
              r'\bsom\b', r'\buma\b', r'\bum\b', r'\bno\b', r'\bo\b',
              r'\ba\b', r'\bvocê\b', r'\bpara\b', r'\bpra\b', r'\bque\b',
              r'\be\b', r'\bvai\b', r'\blá\b', r'\bfaz\b', r'\bpode\b',
              r'\bpor favor\b']:
        termo = re.sub(p, '', termo, flags=re.IGNORECASE)
    termo = re.sub(r'\s+', ' ', termo).strip()

    if not termo:
        falar("Abrindo o Spotify.")
        try:
            os.startfile("spotify:")
        except Exception:
            webbrowser.open("https://open.spotify.com")
        return True

    try:
        from duckduckgo_search import DDGS

        def ddgs_safe(q, n=5):
            try:
                return DDGS().text(q, max_results=n) or []
            except Exception:
                return []

        query = urllib.parse.quote(termo)

        with Spinner():
            results = ddgs_safe(f'"{termo}" spotify track', 8)
        tracks = [r for r in results if 'open.spotify.com/track' in r.get('href', '')]

        if not tracks:
            with Spinner():
                results = ddgs_safe(f'{termo} spotify track', 8)
            tracks = [r for r in results if 'open.spotify.com/track' in r.get('href', '')]

        if tracks:
            for t in tracks:
                href = t.get('href', '')
                if '/track/' in href:
                    track_id = href.split('/track/')[1].split('?')[0].strip('/')
                    nome = t.get('title', termo).split('-')[0].split('|')[0].strip()
                    os.startfile(f"spotify:track:{track_id}")
                    falar(f"Tocando {nome}!")
                    time.sleep(2)
                    pyautogui.press('enter')
                    return True

        falar("Não achei a música exata. Abrindo busca no Spotify.")
        os.startfile(f"spotify:search:{query}")

    except Exception as e:
        print(f"Erro Spotify: {e}")
        os.startfile(f"spotify:search:{urllib.parse.quote(termo)}")

    return True


# ─── Loop principal ───
def main():
    print("=" * 50)
    print("  ASSISTENTE DE VOZ SOPHIE (Edge TTS - Francisca)")
    print("=" * 50)
    print("Comandos: 'youtube <termo>', 'spotify <musica>', 'tocar <musica>', 'pausar', 'pular'")
    print("Para sair: Ctrl+C")
    print()

    falar("Oi! Tudo certo por aqui. O que a gente faz hoje?")

    while True:
        try:
            frase = escutar_microfone()

            if not frase:
                continue

            # 1. YouTube
            if handle_youtube(frase):
                continue

            # 2. Spotify
            if handle_spotify(frase):
                continue

            # 3. Conversa geral com a Sophie (via API)
            resposta = chamar_api(frase)
            falar(resposta)

        except KeyboardInterrupt:
            print("\nEncerrando...")
            falar("Tchau! Ate a proxima.")
            break
        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()