"""
modelo.py — Gerencia a conexão com os modelos de Inteligência Artificial (NVIDIA).
- Chat: Nemotron 3 Ultra (nvidia/nemotron-3-ultra-550b-a55b) via API NVIDIA
- Embeddings: NVIDIA NV-EmbedQA-E5-v5 via API (leve para Vercel serverless)
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage

# Carrega as variáveis do arquivo .env
load_dotenv()

# ─── Configuração NVIDIA ───
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
CHAT_MODEL = os.getenv("CHAT_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")

_chat_model = None
_embedding_model = None


def _get_chat_model() -> ChatOpenAI:
    """Singleton: cria o modelo de chat uma única vez (lazy)."""
    global _chat_model
    if _chat_model is None:
        print(f"Inicializando NVIDIA Chat ({CHAT_MODEL})....")
        _chat_model = ChatOpenAI(
            model=CHAT_MODEL,
            api_key=NVIDIA_API_KEY,
            base_url=NVIDIA_BASE_URL,
            temperature=0.7,
            max_tokens=4096,
            streaming=True,
        )
        # Teste silencioso
        try:
            _chat_model.invoke([HumanMessage(content="oi")])
            print("NVIDIA Chat pronto!")
        except Exception as e:
            print(f"Chat: {e}")
    return _chat_model


def _get_embedding_model() -> OpenAIEmbeddings:
    """Singleton: cria o modelo de embeddings via API NVIDIA (lazy)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Inicializando NVIDIA Embeddings ({EMBEDDING_MODEL})...")
        _embedding_model = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=NVIDIA_API_KEY,
            base_url=NVIDIA_BASE_URL,
        )
        print("NVIDIA Embeddings pronto!")
    return _embedding_model


# ─── API Pública ───
def obter_modelo() -> ChatOpenAI:
    """Retorna o modelo de chat (Nemotron 3 Ultra)."""
    return _get_chat_model()


def obter_embeddings() -> OpenAIEmbeddings:
    """Retorna o modelo de embeddings NVIDIA para memória vetorial."""
    return _embedding_model


def conversar(modelo: ChatOpenAI, texto_pergunta: str) -> str:
    """
    Envia uma pergunta e retorna a resposta completa (não faz print).
    Útil para testes e uso programático.
    """
    mensagem = [HumanMessage(content=texto_pergunta)]
    resposta = modelo.invoke(mensagem)
    return resposta.content


if __name__ == "__main__":
    print("=" * 50)
    print("Teste NVIDIA Nemotron + Embeddings API")
    print("=" * 50)

    try:
        chat = obter_modelo()
        resp = conversar(chat, "Ola! Responda em uma frase: o que e um buraco negro?")
        print(f"\nResposta: {resp}")

        print("\n--- Testando Embeddings ---")
        emb = obter_embeddings()
        vetor = emb.embed_query("teste de embedding")
        print(f"Embedding gerado: {len(vetor)} dimensoes")

    except Exception as erro:
        print(f"\nErro: {erro}")
        import traceback
        traceback.print_exc()
