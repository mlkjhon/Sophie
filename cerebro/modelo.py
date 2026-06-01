"""
modelo.py — Gerencia a conexão com os modelos de Inteligência Artificial.
Tenta usar o Ollama (local) por padrão. Se falhar, usa o Gemini (nuvem) como plano B.
Suporta "streaming" para que a resposta apareça palavra por palavra.
"""

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Carrega as variáveis do arquivo .env
load_dotenv()

def obter_modelo():
    """
    Tenta inicializar o modelo local (Ollama). 
    Se o Ollama não estiver rodando ou der erro, usa o Gemini.
    
    Returns:
        O modelo de IA pronto para ser usado.
    """
    nome_modelo_local = os.getenv("OLLAMA_MODEL", "llama3.1")
    chave_gemini = os.getenv("GEMINI_API_KEY")

    try:
        # Tentamos criar o modelo local com o Ollama
        print(f"🔄 Tentando conectar ao modelo local ({nome_modelo_local})...")
        modelo_local = ChatOllama(model=nome_modelo_local)
        
        # Fazemos um teste rápido "invisível" para ver se o Ollama está ligado
        # Se ele não estiver ligado, isso vai dar erro e pular para o "except"
        modelo_local.invoke([HumanMessage(content="oi")])
        
        print("✅ Conectado ao Ollama (Local)!")
        return modelo_local
        
    except Exception as e:
        print("⚠️ Falha ao conectar no Ollama. O programa está aberto?")
        print("🔄 Mudando para o Gemini (Nuvem) como plano B...")
        
        # Verifica se o usuário colocou a chave do Gemini no .env
        if not chave_gemini or chave_gemini == "sua_chave_aqui_se_for_usar_gemini":
            raise ValueError("❌ Erro: Chave do Gemini não configurada no .env e o Ollama falhou!")
            
        # Retorna o Gemini como fallback
        modelo_gemini = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", # Um modelo rápido e atualizado
            google_api_key=chave_gemini
        )
        print("✅ Conectado ao Gemini (Nuvem)!")
        return modelo_gemini

def conversar(modelo, texto_pergunta):
    """
    Envia uma pergunta para o modelo e imprime a resposta palavra por palavra (streaming).
    
    Args:
        modelo: O modelo de IA inicializado retornado pelo obter_modelo()
        texto_pergunta: A pergunta que você quer fazer em texto
    """
    print(f"\n🗣️ Você: {texto_pergunta}")
    print("🤖 Sophie: ", end="", flush=True)
    
    try:
        # Prepara a mensagem no formato que o LangChain entende
        mensagem = [HumanMessage(content=texto_pergunta)]
        
        # O método .stream() retorna pedaços da resposta assim que são gerados
        for pedaco in modelo.stream(mensagem):
            print(pedaco.content, end="", flush=True)
            
        print("\n") # Pula uma linha no final para ficar organizado
    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao gerar a resposta: {str(e)}")

if __name__ == "__main__":
    # Bloco de Teste: Só é executado se você rodar este arquivo diretamente
    print("=" * 40)
    print("Testando o Cérebro da Sophie")
    print("=" * 40)
    
    try:
        # 1. Carregamos o modelo
        meu_modelo = obter_modelo()
        
        # 2. Fazemos uma pergunta para testar o streaming
        conversar(meu_modelo, "Me explique o que é um buraco negro em apenas uma frase simples.")
        
    except Exception as erro:
        print(f"\n{erro}")
