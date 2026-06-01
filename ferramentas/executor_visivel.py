import sys
import subprocess
import time
import os

def main():
    if len(sys.argv) < 3:
        print("Erro: Faltam argumentos.")
        time.sleep(3)
        return

    arquivo_comando = sys.argv[1]
    arquivo_saida = sys.argv[2]

    # Lê qual o comando que a Sophie quer rodar
    with open(arquivo_comando, "r", encoding="utf-8") as f:
        comando = f.read()

    # Muda a cor do texto do CMD para verde (A) ou azul claro (B)
    os.system("color 0B")
    print(f"\n=======================================================")
    print(f"🤖 [SOPHIE] Executando Comando Autônomo")
    print(f"=======================================================")
    print(f"➜ {comando}\n")

    processo = subprocess.Popen(
        comando, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    saida_completa = ""
    for linha in processo.stdout:
        print(linha, end="")
        saida_completa += linha

    processo.wait()

    # Salva a saída para a mente da Sophie ler depois
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        # Se for vazio, a gente avisa
        if not saida_completa.strip():
            f.write("[Comando executado sem saídas no terminal]")
        else:
            f.write(saida_completa)
        
    print(f"\n=======================================================")
    print(f"✅ Processo finalizado (Código {processo.returncode}). Fechando em 5 segundos...")
    print(f"=======================================================")
    time.sleep(5)

if __name__ == "__main__":
    main()
