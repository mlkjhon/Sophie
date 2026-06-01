"""
arquivos_tool.py — Permite que a Sophie leia documentos do seu computador.
Suporta arquivos PDF e de texto simples (TXT) para ela extrair informações.
"""

import os
from PyPDF2 import PdfReader

def ler_arquivo(caminho_arquivo: str) -> str:
    """
    Lê o conteúdo de um arquivo PDF ou TXT e retorna como texto.
    
    Args:
        caminho_arquivo: O caminho completo ou relativo do arquivo.
        
    Returns:
        O texto extraído do arquivo ou uma mensagem de erro.
    """
    print(f"📄 [Lendo Arquivo] Abrindo '{caminho_arquivo}'...")
    
    # Verifica se o arquivo realmente existe no computador
    if not os.path.exists(caminho_arquivo):
        return f"❌ Erro: O arquivo '{caminho_arquivo}' não foi encontrado."
        
    # Pega a extensão do arquivo (ex: .pdf, .txt) para saber como ler
    extensao = caminho_arquivo.lower().split(".")[-1]
    
    try:
        if extensao == "txt":
            # Abre arquivos de texto normais com codificação UTF-8 (para ler acentos)
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
                return conteudo
                
        elif extensao == "pdf":
            # Abre o PDF em modo de leitura binária ('rb')
            texto_pdf = ""
            leitor = PdfReader(caminho_arquivo)
            
            # Passa por todas as páginas do PDF extraindo o texto
            for pagina in leitor.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_pdf += texto_pagina + "\n"
                    
            return texto_pdf
            
        else:
            return f"❌ Erro: Formato '{extensao}' ainda não é suportado. Use PDF ou TXT."
            
    except Exception as e:
        return f"❌ Erro ao tentar ler o arquivo: {str(e)}"

def escrever_arquivo(argumentos: str) -> str:
    """
    Escreve ou sobrescreve um arquivo de texto.
    Obrigatório passar no formato: Caminho | Conteudo
    Exemplo: C:\\Users\\Usuario\\Documents\\nota.txt | Comprar pão e leite
    """
    print(f"✍️ [Escrevendo Arquivo] Processando comando...")
    try:
        partes = argumentos.split('|', 1)
        if len(partes) < 2:
            return "❌ Formato inválido. Use: CaminhoCompleto | Conteudo"
            
        caminho = partes[0].strip()
        conteudo = partes[1].strip()
        
        # Cria as pastas pai caso não existam
        diretorio = os.path.dirname(caminho)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio)
            
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
        return f"✅ Arquivo salvo com sucesso em '{caminho}'."
    except Exception as e:
        return f"❌ Erro ao tentar salvar o arquivo: {str(e)}"

if __name__ == "__main__":
    # Teste de leitura de arquivos
    print("=" * 40)
    print("Testando Ferramenta: Leitura de Arquivos")
    print("=" * 40)
    
    # 1. Cria um arquivo de teste rápido só para termos o que ler
    arquivo_teste = "teste_sophie.txt"
    with open(arquivo_teste, "w", encoding="utf-8") as f:
        f.write("Este é um documento confidencial.\nA senha do Wi-Fi é: sophie2024")
        
    # 2. Testa a ferramenta lendo o arquivo que acabamos de criar
    resultado = ler_arquivo(arquivo_teste)
    
    print("\nO que a ferramenta leu do arquivo:")
    print("-" * 30)
    print(resultado)
    print("-" * 30)
    
    # Limpa o arquivo de teste depois
    if os.path.exists(arquivo_teste):
        os.remove(arquivo_teste)
