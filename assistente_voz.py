import speech_recognition as sr
import pygame
import requests
import os
import time
import subprocess
import tempfile
import sys
import re

# Importa o módulo do backend do YouTube
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend_youtube'))
from mecanismo_busca import buscar_videos_no_youtube, disparar_abertura_do_video

# Inicializa o mixer de áudio do pygame
pygame.mixer.init()

# URL da nossa própria API local
API_URL = "http://localhost:8000/chat"

import threading

class Spinner:
    def __init__(self):
        self.spinner_chars = ['|', '/', '-', '\\']
        self.delay = 0.1
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f'\r{self.spinner_chars[i % 4]}')
            sys.stdout.flush()
            time.sleep(self.delay)
            i += 1
        sys.stdout.write('\r \r')
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.running = False
        if self.thread:
            self.thread.join()

def falar(texto):
    """Faz a Sophie falar em voz alta usando Edge-TTS (Voz Neural ultra realista)."""
    print(f" Sophie: {texto}")
    
    if not texto.strip():
        return
        
    try:
        # Pega o modo global atual para decidir a voz
        modo = globals().get("modo_atual", "conversa")
        voz = "pt-BR-AntonioNeural" if modo == "jarvis" else "pt-BR-FranciscaNeural"

        # Salva o texto num arquivo para evitar problema com aspas no comando CLI
        fd, path_txt = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        with open(path_txt, "w", encoding="utf-8") as f:
            f.write(texto)
            
        arquivo_temp = "resposta_sophie.mp3"
        
        # Chama a API da Microsoft
        cmd = f'"{sys.executable}" -m edge_tts -f "{path_txt}" --voice {voz} --write-media "{arquivo_temp}"'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Toca o áudio gerado
        pygame.mixer.music.load(arquivo_temp)
        pygame.mixer.music.play()
        
        # Espera o áudio terminar de tocar
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Libera o arquivo e apaga
        pygame.mixer.music.unload()
        try:
            os.remove(arquivo_temp)
            os.remove(path_txt)
        except:
            pass
    except Exception as e:
        print(f"Erro ao tentar falar: {e}")

def escutar_microfone():
    """Ouve o microfone e tenta reconhecer a fala."""
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.5 
    
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 300  
    
    with sr.Microphone() as source:
       
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        print("\n [Ouvindo...] Pode falar.")
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            
            with Spinner():
                texto_falado = recognizer.recognize_google(audio, language='pt-BR').lower()
            
            # Filtro Fonético Avançado: Corrige o Google STT que tenta traduzir jargões de TI para português
            correcoes = {
                # Jogos e Apps
                "valente": "valorant",
                "valera": "valorant",
                "tocar valente": "abrir valorant",
                "chati g p t": "chatgpt",
                "chat e g p t": "chatgpt",
                "espotifai": "spotify",
                "spoti": "spotify",
                "spotifyfy": "spotify",
                
                # Jargões de Programação
                "backe e ba": "backend",
                "back end": "backend",
                "beck end": "backend",
                "front end": "frontend",
                "fronte end": "frontend",
                "full stack": "fullstack",
                "ful steck": "fullstack",
                "dê bug": "debug",
                "de bugar": "debugar",
                "banco de dados": "database",
                "da tá base": "database",
                "term": "terminal",
                
                # Linguagens e Frameworks
                "paiton": "python",
                "pai ton": "python",
                "pai tão": "python",
                "java script": "javascript",
                "javiscript": "javascript",
                "tai pes cript": "typescript",
                "type script": "typescript",
                "re act": "react",
                "riect": "react",
                "next d e s": "nextjs",
                "next js": "nextjs",
                "n d e s": "nodejs",
                "node js": "nodejs",
                "v o e": "vue",
                "v u e": "vue",
                "teio in de": "tailwindcss",
                "tailwind": "tailwindcss",
                
                # Ferramentas
                "v i s code": "vscode",
                "vs code": "vscode",
                "v s code": "vscode",
                "git rub": "github",
                "git hub": "github",
                "do que r": "docker",
                "dóquer": "docker",
                "ku ber netes": "kubernetes",
                "a p i": "api"
            }
            
            for errado, certo in correcoes.items():
                texto_falado = texto_falado.replace(errado, certo)
                
            print(f" Você: {texto_falado}")
            return texto_falado
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"❌ Erro de conexão com o STT: {e}")
            return None

def enviar_para_cerebro(texto, modo_atual):
    """Envia o texto com regras estritas de conversação rápida, informando o modo."""
    if modo_atual == "jarvis":
        texto_com_regras = (
            texto +
            "\n\n[REGRA DE SISTEMA (MODO VOZ ATIVADO - JARVIS)]: Suas respostas verbais devem ser curtas, diretas e confirmatórias. Você não deve ler blocos de código em voz alta, mas sim confirmar a execução e enviar o código gerado em texto/tela.\n"
            "INSTRUÇÕES DE RESPOSTA VOCAL:\n"
            "Módulo 1 (Front-end - 'criar tela'): Responda apenas: 'Estrutura visual renderizada, Senhor. Código HTML e CSS enviado para o seu terminal.'\n"
            "Módulo 2 (Back-end - 'criar lógica'): Responda apenas: 'Classes Java compiladas e integração estruturada, Senhor.'\n"
            "Módulo 3 (Arquitetura de Dados - 'modelar banco'): Responda apenas: 'Esquema do PostgreSQL atualizado. Queries prontas para execução.'\n"
            "Módulo 4 (Captação - 'estruturar funil'): Responda apenas: 'Funil de captação alinhado e rotas de salvamento no banco configuradas, Senhor.'\n"
            "Módulo 5 (Debugging - 'encontre o erro'): Responda apenas: 'Varredura de diagnóstico iniciada. Aguardando o log de erro na interface de texto.'\n"
            "Para outros comandos: Inicie a resposta com uma confirmação curta (Ex: 'Sim, Senhor', 'Em andamento', 'Processando') e forneça a saída técnica na interface de texto."
        )
    elif modo_atual == "matematica":
        texto_com_regras = (
            texto +
            "\n\n[REGRA DE SISTEMA (MODO VOZ ATIVADO - MATEMÁTICA)]: Você está operando via comando de voz (speech-to-text). "
            "Sua resposta deve ser adaptada para máxima eficiência auditiva, já que ouvir cálculos longos é cansativo.\n"
            "DIRETRIZES DE RESPOSTA VOCAL PARA MATEMÁTICA:\n"
            "1. Confirmação Rápida: Inicie sempre confirmando a recepção (Ex: 'Processando os números, Senhor', 'Calculando a equação...').\n"
            "2. Foco no Resultado: Na sua resposta falada, priorize entregar o Passo 5 (A resposta final) de forma clara, direta e mastigada.\n"
            "3. Omissão de Fórmulas Longas na Fala: Evite narrar equações longas, frações complexas ou variáveis matemáticas linha por linha (Passo 2 e 3). Resuma o processo logicamente na voz e indique que 'os detalhes do cálculo estão disponíveis no terminal/tela'.\n"
            "4. Se o usuário pedir apenas uma conta simples, entregue o resultado imediatamente."
        )
    else:
        texto_com_regras = (
            texto + 
            "\n\n[REGRA DE SISTEMA (MODO VOZ ATIVADO)]: Você está numa chamada de voz com o usuário. "
            "Não seja excessivamente breve, responda a pergunta com detalhes satisfatórios e naturais (você pode gerar textos maiores). "
            "NUNCA crie listas com marcadores markdown, NUNCA mande blocos de código grandes pela voz. "
            "SE O USUÁRIO PEDIR RECOMENDAÇÃO DE MÚSICAS: Sugira músicas com base em gêneros bons para programar ou relaxar (Rock, Lo-Fi, Eletrônica, etc). Diga a ele: 'Se quiser, basta me dizer para tocar essa música no Spotify que eu abro para você!'. "
            "SE O USUÁRIO PEDIR ALGO RELACIONADO À AGENDA: Responda adequadamente sobre a agenda. Não misture agenda com música a não ser que façam sentido na mesma frase. "
            "SEMPRE termine sua resposta com um 'gancho' educado e comum. Exemplos: 'Posso te ajudar com algo mais?', 'Precisa de mais alguma coisa?', 'O que mais vamos fazer agora?'."
        )
    
    try:
        with Spinner():
            resposta = requests.post(API_URL, json={"texto": texto_com_regras, "modo": modo_atual}, timeout=600)
        if resposta.status_code == 200:
            return resposta.json().get("resposta", "Erro.")
        else:
            return f"Erro no servidor: {resposta.status_code}."
    except Exception as e:
        return "Desculpe, a conexão com o cérebro caiu."

def main():
    global modo_atual
    print("="*50)
    print("  ASSISTENTE DE VOZ NEURAL SOPHIE")
    print("="*50)
    print("Para parar, aperte Ctrl+C.")
    
    modo_atual = "conversa"
    falar("Oi! A conexão tá ótima, o que vamos fazer hoje?")
    
    while True:
        try:
            frase = escutar_microfone()
            
            if frase:
                # INTERCEPTADOR DE TROCA DE MODO
                if "modo matemática" in frase or "modo matematica" in frase:
                    modo_atual = "matematica"
                    falar("Iniciando transição de modos.")
                    time.sleep(1)
                    falar("Modo Matemática carregado com sucesso. Como posso ajudar com seus cálculos?")
                    continue
                    
                if "modo jarvis" in frase or "modo programador" in frase:
                    modo_atual = "jarvis"
                    falar("Iniciando transição de modos.")
                    time.sleep(1)
                    falar("Modo Jarvis carregado. Sistemas de programação online.")
                    continue

                if "modo conversa" in frase or "modo prosa" in frase:
                    modo_atual = "conversa"
                    falar("Iniciando transição de modos.")
                    time.sleep(1)
                    falar("Modo conversa carregado. Vamos bater um papo!")
                    continue
                
                # INTERCEPTADOR DE COMANDOS DO YOUTUBE
                if "youtube" in frase or "pesquisar vídeo" in frase or "buscar vídeo" in frase:
                    falar("Entendido. Acessando o sistema do YouTube...")
                    
                    # Limpa as palavras de comando usando Regex (evita cortar pedaços de outras palavras, ex: 'no' dentro de 'node')
                    termo = frase
                    palavras_remover = [r'\bpesquisar\b', r'\bbuscar\b', r'\bprocurar\b', r'\byoutube\b', r'\bvídeos?\b', r'\bsobre\b', r'\bpor\b', r'\bno\b', r'\bum\b', r'\bo\b', r'\ba\b', r'\babrir\b', r'\babra\b', r'\bquero\b', r'\bver\b', r'\bpesquise\b', r'\bde\b', r'\bdo\b', r'\bda\b']
                    for p in palavras_remover:
                        termo = re.sub(p, '', termo, flags=re.IGNORECASE)
                    termo = re.sub(r'\s+', ' ', termo).strip()
                    
                    if not termo:
                        falar("Abrindo a página inicial do YouTube para você.")
                        import webbrowser
                        webbrowser.open("https://www.youtube.com")
                        continue
                        
                    falar(f"Buscando conteúdos relevantes sobre {termo}.")
                    resultado = buscar_videos_no_youtube(termo)
                    
                    if resultado and resultado["lista_videos"]:
                        videos = resultado["lista_videos"]
                        primeiro_video = videos[0]
                        falar(f"Pronto! Encontrei o vídeo {primeiro_video['titulo']} do canal {primeiro_video['canal']}. Abrindo na sua tela agora.")
                        disparar_abertura_do_video(primeiro_video['link'])
                    else:
                        falar("Infelizmente não encontrei nenhum conteúdo avançado correspondente a esse termo.")
                    continue
                    
                # INTERCEPTADOR DE COMANDOS DO SPOTIFY
                gatilhos_acao = ["abra", "abre", "abrir", "tocar", "toque", "ouvir", "coloca", "colocar", "pesquisar", "buscar"]
                gatilhos_diretos = ["toca ", "toque ", "tocar ", "quero ouvir ", "queria ouvir ", "coloca ", "pula ", "pular ", "próxima", "passa a música", "pausar", "pause ", "pare "]
                
                eh_spotify = False
                if "spotify" in frase and any(v in frase for v in gatilhos_acao):
                    eh_spotify = True
                elif any(g in frase for g in gatilhos_diretos):
                    eh_spotify = True
                elif "música" in frase and any(v in frase for v in ["tocar", "toca", "pausar", "parar", "ouvir"]):
                    eh_spotify = True

                if eh_spotify:
                    
                    if any(p in frase for p in ["pause", "pausar", "pare", "parar", "pausa"]):
                        falar("Pausando o Spotify.")
                        import pyautogui
                        pyautogui.press('playpause')
                        continue
                        
                    if any(p in frase for p in ["pular", "pula", "próxima", "passar", "passa", "avançar"]):
                        falar("Pulando a música.")
                        import pyautogui
                        pyautogui.press('nexttrack')
                        continue

                    falar("Entendido. Conectando ao Spotify...")
                    termo_spotify = frase
                    palavras_remover_spotify = [r'\bspotify\b', r'\bquero\b', r'\bqueria\b', r'\bouvir\b', r'\bcoloca\b', r'\btocar\b', r'\btoque\b', r'\btoca\b', r'\babrir\b', r'\babra\b', r'\babre\b', r'\bmúsica\b', r'\bsom\b', r'\buma\b', r'\bum\b', r'\bno\b', r'\bo\b', r'\ba\b', r'\bvocê\b', r'\bpara\b', r'\bpra\b', r'\bque\b', r'\be\b', r'\bvai\b', r'\blá\b', r'\bfaz\b', r'\bpode\b', r'\bpor favor\b']
                    for p in palavras_remover_spotify:
                        termo_spotify = re.sub(p, '', termo_spotify, flags=re.IGNORECASE)
                    termo_spotify = re.sub(r'\s+', ' ', termo_spotify).strip()

                    import webbrowser, urllib.parse, os, pyautogui as _pag, time as _t
                    
                    if not termo_spotify:
                        falar("Abrindo o aplicativo do Spotify.")
                        try:
                            os.startfile("spotify:")
                        except Exception:
                            webbrowser.open("https://open.spotify.com")
                        continue

                    print(f"  [Spotify] Buscando por: '{termo_spotify}'")
                    query = urllib.parse.quote(termo_spotify)
                    try:
                        from ddgs import DDGS

                        def _ddgs(query, n=5):
                            """DDGS seguro — retorna lista vazia em vez de lançar exceção."""
                            try:
                                return DDGS().text(query, max_results=n) or []
                            except Exception:
                                return []

                        def _tocar_track(url_track, nome):
                            _id = url_track.split("/track/")[1].split("?")[0].strip("/")
                            os.startfile(f"spotify:track:{_id}")
                            falar(f"Tocando {nome}!")
                            _t.sleep(3)
                            _pag.press('enter')

                        def _remover_acentos(texto):
                            import unicodedata
                            return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

                        def _buscar_track(termo):
                            """Busca a track com match exato ou fallback aberto."""
                            termo_quoted = f'"{termo}"'
                            
                            # Tentativa 1: busca aberta com aspas
                            with Spinner():
                                rs_aberto = _ddgs(f"{termo_quoted} spotify track", 8)
                            rs = [r for r in rs_aberto if "open.spotify.com/track" in r.get('href', '')]
                            
                            # Tentativa 2: sem aspas
                            if not rs:
                                with Spinner():
                                    rs_aberto = _ddgs(f"{termo} spotify track", 8)
                                rs = [r for r in rs_aberto if "open.spotify.com/track" in r.get('href', '')]

                            if not rs:
                                return False

                            melhor = None
                            termo_lower = _remover_acentos(termo.lower())
                            
                            # Match exato no título
                            for r in rs:
                                titulo = _remover_acentos(r.get('title', '').lower())
                                href = r.get('href', '')
                                if "/track/" in href and titulo.startswith(termo_lower):
                                    melhor = r
                                    break
                                    
                            # Fallback: contém a primeira palavra
                            if not melhor:
                                palavra_chave = termo_lower.split()[0]
                                for r in rs:
                                    titulo = _remover_acentos(r.get('title', '').lower())
                                    if "/track/" in r.get('href', '') and palavra_chave in titulo:
                                        melhor = r
                                        break
                                        
                            # Último recurso: primeira track
                            if not melhor:
                                melhor = rs[0]

                            if melhor:
                                url = melhor['href']
                                nome = melhor.get('title', termo).split("-")[0].split("|")[0].strip()
                                _tocar_track(url, nome)
                                return True
                            return False

                        # Etapa 1 — detectar artista vs música
                        falar("Um segundo...")
                        
                        # Busca aberta por artista no Spotify
                        with Spinner():
                            res_artista = _ddgs(f"{termo_spotify} spotify artist", 4)
                        
                        eh_artista = False
                        termo_norm = _remover_acentos(termo_spotify.lower())
                        
                        for res in res_artista:
                            if "/artist/" in res.get('href', ''):
                                titulo_pg = _remover_acentos(res.get('title', '').lower())
                                nome_pg = titulo_pg.split("|")[0].split("-")[0].strip()
                                palavras = [p for p in termo_norm.split() if len(p) > 2]
                                if palavras and all(p in nome_pg for p in palavras):
                                    eh_artista = True
                                    break

                        if eh_artista:
                            # Etapa 2 — artista: buscar músicas MAIS TOCADAS via busca aberta (ranqueada por popularidade)
                            with Spinner():
                                # Busca aberta no Google/DDG: retorna o que mais aparece em artigos de "top músicas"
                                tracks_raw = _ddgs(f"{termo_spotify} melhores músicas spotify", 10)

                            seen, opcoes = set(), []
                            for t in tracks_raw:
                                href = t.get('href', '')
                                titulo = t.get('title', '')
                                # Filtra apenas URLs de tracks do Spotify
                                if "open.spotify.com/track/" in href or "open.spotify.com/intl" in href:
                                    nm = titulo.split("-")[0].replace("|","").strip()
                                    if nm.lower() not in seen:
                                        seen.add(nm.lower())
                                        opcoes.append((nm, href))
                                if len(opcoes) == 3:
                                    break

                            # Fallback: se a busca aberta não achou tracks suficientes, tenta direto
                            if len(opcoes) < 2:
                                with Spinner():
                                    tracks_raw2 = _ddgs(f"site:open.spotify.com/track {termo_spotify}", 6)
                                for t in tracks_raw2:
                                    nm = t['title'].split("-")[0].replace("|","").strip()
                                    if nm.lower() not in seen and "/track/" in t.get('href', ''):
                                        seen.add(nm.lower())
                                        opcoes.append((nm, t['href']))
                                    if len(opcoes) == 3:
                                        break

                            if opcoes:
                                nomes = [o[0] for o in opcoes]
                                lista = ", ".join(nomes[:-1]) + f" ou {nomes[-1]}" if len(nomes) > 1 else nomes[0]
                                falar(f"Aqui estão as mais tocadas de {termo_spotify}: {lista}. Qual você quer?")
                                escolha = escutar_microfone()
                                if escolha and not any(p in escolha for p in ["qualquer","tanto faz","primeira"]):
                                    if not _buscar_track(f"{escolha} {termo_spotify}"):
                                        _buscar_track(escolha)
                                else:
                                    _tocar_track(opcoes[0][1], opcoes[0][0])
                            else:
                                falar(f"Qual música de {termo_spotify} você quer ouvir?")
                                escolha = escutar_microfone()
                                if escolha:
                                    if not _buscar_track(f"{escolha} {termo_spotify}"):
                                        _buscar_track(escolha)
                                else:
                                    os.startfile(f"spotify:search:{query}")
                        else:
                            # Etapa 3 — música específica: tocar direto
                            if not _buscar_track(termo_spotify):
                                falar("Não encontrei essa música. Abrindo busca no Spotify.")
                                os.startfile(f"spotify:search:{query}")

                    except Exception as e:
                        print(f"Erro Spotify: {e}")
                        os.startfile(f"spotify:search:{query}")
                    continue


                # Se não for comando do YouTube nem do Spotify, segue para o cérebro normal da Sophie
                resposta = enviar_para_cerebro(frase, modo_atual)
                falar(resposta)
                    
        except KeyboardInterrupt:
            print("\n Encerrando assistente de voz...")
            break
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
