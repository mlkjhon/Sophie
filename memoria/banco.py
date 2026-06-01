"""
banco.py — Gerencia a memória de longo prazo do Sophie.
Salva conversas e informações em um banco de dados vetorial (ChromaDB),
permitindo que a Sophie lembre de você entre diferentes sessões.
"""

import os
from datetime import datetime
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Pasta onde o banco de dados será salvo fisicamente no seu PC
PASTA_BANCO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dados", "memoria_db")

def obter_embeddings():
    """
    Retorna o modelo de embeddings do Ollama.
    Embeddings transformam texto em números para a IA entender o 'significado' das frases.
    """
    # Usamos o modelo 'nomic-embed-text' porque é super leve e focado apenas nisso.
    return OllamaEmbeddings(model="nomic-embed-text")

def obter_banco():
    """
    Conecta ao banco de dados ChromaDB. Se ele não existir, cria um novo automaticamente.
    
    Returns:
        O banco de dados vetorial pronto para uso.
    """
    return Chroma(
        collection_name="memorias_sophie",
        embedding_function=obter_embeddings(),
        persist_directory=PASTA_BANCO
    )

def salvar_memoria(texto: str, categoria: str = "fato"):
    """
    Salva uma informação na memória da Sophie.
    
    Args:
        texto: A frase ou informação a ser lembrada.
        categoria: O tipo de memória (ex: "preferencia", "conversa").
    """
    banco = obter_banco()
    
    # Metadados ajudam a organizar ou filtrar as memórias no futuro
    metadados = {
        "categoria": categoria,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # O add_texts transforma o texto em vetor (números) e salva na pasta
    banco.add_texts(texts=[texto], metadatas=[metadados])
    print(f"💾 [Memória Guardada] {texto}")

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
    
    # similarity_search encontra os textos cujo significado mais se aproxima da pergunta
    resultados = banco.similarity_search(pergunta, k=quantidade)
    
    # Extrai apenas o texto dos resultados
    memorias = [doc.page_content for doc in resultados]
    return memorias

if __name__ == "__main__":
    # Bloco de Teste: Só roda se você executar este arquivo diretamente
    print("=" * 40)
    print("Testando a Memória da Sophie")
    print("=" * 40)
    
    try:
        # 1. Salvar uma memória
        salvar_memoria("Eu prefiro meu café sem açúcar.", categoria="preferencia")
        
        # 2. Buscar algo relacionado a café
        print("\n🔍 Buscando informações sobre café...")
        lembrancas = buscar_memoria("Como eu gosto do meu café?")
        
        for i, lembranca in enumerate(lembrancas, 1):
            print(f"🧠 Lembrei ({i}): {lembranca}")
            
    except Exception as erro:
        print(f"\n❌ Erro no teste de memória: {erro}")
