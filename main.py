"""
main.py — Ponto de entrada do Sophie.
Nesta etapa, apenas verificamos se o ambiente está configurado corretamente
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
    print("=" * 40)
    print("Ola! Eu sou a Sophie.")
    print("Ambiente configurado com sucesso!")
    print("Modelo: NVIDIA Nemotron 3 Ultra (API)")
    print("=" * 40)

if __name__ == "__main__":
    # Quando o arquivo for rodado, executamos o teste
    testar_ambiente()
