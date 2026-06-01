import speech_recognition as sr
import pygame
import requests
import os
import time
import subprocess
import tempfile

# Inicializa o mixer de áudio do pygame
pygame.mixer.init()

# URL da nossa própria API local
API_URL = "http://localhost:8000/chat"

def falar(texto):
    """Faz a Sophie falar em voz alta usando Edge-TTS (Voz Neural ultra realista)."""
    print(f"🤖 Sophie diz: {texto}")
    
    if not texto.strip():
        return
        
    try:
        # Salva o texto num arquivo para evitar problema com aspas no comando CLI
        fd, path_txt = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        with open(path_txt, "w", encoding="utf-8") as f:
            f.write(texto)
            
        arquivo_temp = "resposta_sophie.mp3"
        
        # Chama a API da Microsoft (Voz Francisca, feminina realista)
        cmd = f'edge-tts -f "{path_txt}" --voice pt-BR-FranciscaNeural --write-media "{arquivo_temp}"'
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
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("\n🎧 [Ouvindo...] Pode falar.")
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            print("⏳ [Pensando...]")
            
            texto_falado = recognizer.recognize_google(audio, language='pt-BR').lower()
            
            # Filtro de audição (Correções de nomes em inglês e jargões que o Google STT erra)
            correcoes = {
                "valente": "valorant",
                "valera": "valorant",
                "term": "terminal",
                "chati g p t": "chatgpt",
                "espotifai": "spotify",
                "spoti": "spotify",
                "tocar valente": "abrir valorant"
            }
            
            for errado, certo in correcoes.items():
                texto_falado = texto_falado.replace(errado, certo)
                
            print(f"👤 Você disse: {texto_falado}")
            return texto_falado
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"❌ Erro de conexão com o STT: {e}")
            return None

def enviar_para_cerebro(texto):
    """Envia o texto com regras estritas de conversação rápida."""
    # INJEÇÃO DE PERSONALIDADE DE VOZ E VELOCIDADE
    texto_com_regras = (
        texto + 
        "\n\n[REGRA DE SISTEMA (MODO VOZ ATIVADO)]: Você está numa chamada de voz com o usuário. "
        "Não seja excessivamente breve, responda a pergunta com detalhes satisfatórios e naturais (você pode gerar textos maiores). "
        "NUNCA crie listas com marcadores markdown, NUNCA mande blocos de código grandes pela voz (apenas crie os arquivos se ele pedir código). "
        "SEMPRE termine sua resposta com um 'gancho' educado e comum. Exemplos: 'Posso te ajudar com algo mais?', 'Precisa de mais alguma coisa?', 'O que mais vamos fazer agora?'."
    )
    
    try:
        resposta = requests.post(API_URL, json={"texto": texto_com_regras}, timeout=120)
        if resposta.status_code == 200:
            return resposta.json().get("resposta", "Erro.")
        else:
            return f"Erro no servidor: {resposta.status_code}."
    except Exception as e:
        return "Desculpe, a conexão com o cérebro caiu."

def main():
    print("="*50)
    print("🎙️  ASSISTENTE DE VOZ NEURAL SOPHIE")
    print("="*50)
    print("Para parar, aperte Ctrl+C.")
    
    falar("Oi! A conexão tá ótima, o que vamos fazer hoje?")
    
    while True:
        try:
            frase = escutar_microfone()
            
            if frase:
                resposta = enviar_para_cerebro(frase)
                falar(resposta)
                    
        except KeyboardInterrupt:
            print("\n🛑 Encerrando assistente de voz...")
            break
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
