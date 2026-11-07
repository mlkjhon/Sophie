"""
banco.py — Gerencia a memória de longo prazo da Sophie.
Salva conversas e informações no Supabase pgvector,
permitindo que a Sophie lembre de você entre diferentes sessões.
Usa embeddings locais (sentence-transformers/all-MiniLM-L6-v2).
"""

import os
from datetime import datetime
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from dados.db import POSTGRES_URL

# Configuração do PGVector
COLLECTION_NAME = "memorias_sophie"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_model = None
_vector_store = None


def _get_embedding_model() -> HuggingFaceEmbeddings:
    """Singleton: cria o modelo de embeddings local uma única vez (lazy)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Inicializando Embeddings local ({EMBEDDING_MODEL})...")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embeddings local pronto!")
    return _embedding_model


def _get_vector_store() -> PGVector:
    """Singleton: cria o vector store PGVector uma única vez (lazy)."""
    global _vector_store
    if _vector_store is None:
        print("Conectando ao Supabase pgvector...")
        _vector_store = PGVector(
            embeddings=_get_embedding_model(),
            collection_name=COLLECTION_NAME,
            connection=POSTGRES_URL,
            use_jsonb=True,
        )
        print("PGVector pronto!")
    return _vector_store


def obter_banco() -> PGVector:
    """Retorna o vector store PGVector pronto para uso."""
    return _get_vector_store()


def salvar_memoria(texto: str, categoria: str = "fato"):
    """
    Salva uma informação na memória da Sophie.

    Args:
        texto: A frase ou informação a ser lembrada.
        categoria: O tipo de memória (ex: "preferencia", "conversa").
    """
    banco = obter_banco()

    metadados = {
        "categoria": categoria,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    banco.add_texts(texts=[texto], metadatas=[metadados])
    print(f"[Memoria Guardada] {texto}")


def buscar_memoria(pergunta: str, quantidade: int = 3):
    """
    Busca no banco as memórias mais relevantes para a pergunta atual.

    Args:
        pergunta: A pergunta que você fez (para achar coisas relacionadas).
        quantidade: Quantas memórias trazer (padrão 3).

    Returns:
        Uma lista de textos com as memórias encontradas.
    """
    banco = obter_banco()

    resultados = banco.similarity_search(pergunta, k=quantidade)
    memorias = [doc.page_content for doc in resultados]
    return memorias


def inicializar_pgvector():
    """
    Cria a extensão pgvector e a tabela no Supabase.
    Execute uma vez para configurar o banco.
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(POSTGRES_URL)
    with engine.connect() as conn:
        # Ativa extensão pgvector
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("Extensao pgvector ativada!")

    # O PGVector cria a tabela automaticamente no primeiro add_texts
    _ = obter_banco()
    print("Tabela de memorias criada/verificada!")


if __name__ == "__main__":
    print("=" * 40)
    print("Testando a Memoria da Sophie (PGVector)")
    print("=" * 40)

    try:
        # Inicializa pgvector no Supabase
        inicializar_pgvector()

        # 1. Salvar uma memória
        salvar_memoria("Eu prefiro meu cafe sem acucar.", categoria="preferencia")

        # 2. Buscar algo relacionado a café
        print("\nBuscando informacoes sobre cafe...")
        lembrancas = buscar_memoria("Como eu gosto do meu cafe?")

        for i, lembranca in enumerate(lembrancas, 1):
            print(f"Lembrei ({i}): {lembranca}")

    except Exception as erro:
        print(f"\nErro no teste de memoria: {erro}")
        import traceback
        traceback.print_exc()
