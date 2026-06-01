"""
main.py — Ponto de entrada do Sophie.
Nesta primeira etapa, apenas verificamos se o ambiente está configurado corretamente
carregando as variáveis de ambiente.
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def testar_ambiente():
    """
    Verifica se o ambiente básico foi carregado e dá um oi.
    """
    modelo = os.getenv("OLLAMA_MODEL", "Não definido")
    
    print("=" * 40)
    print("🤖 Olá! Eu sou a Sophie.")
    print("✅ Ambiente configurado com sucesso!")
    print(f"🧠 Modelo local configurado para: {modelo}")
    print("=" * 40)

if __name__ == "__main__":
    # Quando o arquivo for rodado, executamos o teste
    testar_ambiente()
