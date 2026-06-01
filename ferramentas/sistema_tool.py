"""
sistema_tool.py — Permite que a Sophie interaja com o sistema operacional (Windows).
"""
import os
import subprocess

def abrir_aplicativo(caminho_ou_nome: str):
    """
    Abre um aplicativo ou caminho no PC do usuário.
    Tente passar o nome do executável (ex: 'calc', 'notepad', 'chrome', 'msedge') ou o caminho completo de uma pasta/arquivo.
    """
    print(f"🖥️ [Sistema] Tentando abrir: {caminho_ou_nome}")
    try:
        nome_limpo = caminho_ou_nome.lower().strip()
        if nome_limpo in ["terminal", "cmd", "prompt"]:
            caminho_ou_nome = "cmd.exe"
            
        # No Windows, 'start' pelo os.system ou shell=True resolve a maioria dos apps
        # O uso de strings brutas evita problemas com espaços
        subprocess.Popen(f'start "" "{caminho_ou_nome}"', shell=True)
        return f"✅ Comando enviado para abrir '{caminho_ou_nome}'"
    except Exception as e:
        return f"❌ Erro ao tentar abrir aplicativo: {e}"

def listar_arquivos(diretorio: str):
    """
    Lista os arquivos e pastas dentro de um diretório específico.
    Use barras duplas \\ ou barra normal / para caminhos no Windows. Ex: C:/Users
    """
    print(f"📁 [Sistema] Listando arquivos em: {diretorio}")
    try:
        itens = os.listdir(diretorio)
        if not itens:
            return f"A pasta '{diretorio}' está vazia."
        
        # Pega apenas os 20 primeiros para não estourar o limite de tokens do LLM
        resumo = f"Arquivos em {diretorio} (Mostrando máx 20):\n"
        for item in itens[:20]:
            caminho_completo = os.path.join(diretorio, item)
            tipo = "[Pasta]" if os.path.isdir(caminho_completo) else "[Arquivo]"
            resumo += f"- {tipo} {item}\n"
            
        if len(itens) > 20:
            resumo += f"...e mais {len(itens) - 20} itens."
            
        return resumo
    except Exception as e:
        return f"❌ Erro ao listar arquivos (Verifique se o caminho existe e se o formato está correto): {e}"
