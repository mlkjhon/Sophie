"""
terminal_tool.py — Dá superpoderes para a Sophie rodar comandos no terminal do usuário.
Isso permite que ela aja como uma programadora, instalando pacotes, compilando e rodando códigos em qualquer linguagem.
"""
import subprocess
import os
import tempfile

def executar_comando_terminal(comando: str) -> str:
    """
    Executa um comando no terminal do Windows (PowerShell/CMD) abrindo uma JANELA VISÍVEL para o usuário.
    """
    print(f"💻 [Terminal] Abrindo janela visível para executar: {comando}")
    try:
        # Cria arquivos temporários para passar o comando sem problemas de aspas
        fd_cmd, path_cmd = tempfile.mkstemp(suffix=".cmd.txt")
        fd_out, path_out = tempfile.mkstemp(suffix=".out.txt")
        os.close(fd_cmd)
        os.close(fd_out)
        
        with open(path_cmd, "w", encoding="utf-8") as f:
            f.write(comando)
            
        caminho_executor = os.path.join(os.path.dirname(__file__), "executor_visivel.py")
        
        # O start "Titulo" /WAIT faz o terminal principal (Python) pausar até que a nova janela seja fechada
        comando_start = f'start "Terminal da Sophie" /WAIT python "{caminho_executor}" "{path_cmd}" "{path_out}"'
        
        # Executa abrindo o novo terminal
        subprocess.run(comando_start, shell=True)
        
        # Assim que a janela fechar, nós lemos a saída
        saida_completa = ""
        if os.path.exists(path_out):
            with open(path_out, "r", encoding="utf-8") as f:
                saida_completa = f.read()
                
        # Limpa o lixo
        try:
            os.remove(path_cmd)
            os.remove(path_out)
        except:
            pass
        
        # Trunca para não estourar a memória (context window) do modelo
        if len(saida_completa) > 3000:
            saida_completa = saida_completa[-3000:] + "\n... (saída truncada)"
            
        return f"✅ Executado com sucesso. Saída do Terminal:\n{saida_completa}"
        
    except Exception as e:
        return f"❌ Erro crítico no terminal: {e}"
