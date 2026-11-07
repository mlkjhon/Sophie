"""
google_auth.py — Gerencia a autenticação com o Google.
Abre o navegador para você fazer login com segurança e salva a sessão para a Sophie.
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# As permissões que a Sophie vai ter: Ler/Modificar emails e Ler/Criar eventos
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

def obter_credenciais():
    """Faz o login com o Google e retorna as credenciais."""
    creds = None
    caminho_token = 'token.json'
    caminho_credenciais = 'credentials.json'

    # Verifica se já temos o login salvo de uma vez anterior
    if os.path.exists(caminho_token):
        creds = Credentials.from_authorized_user_file(caminho_token, SCOPES)
        
    # Se não temos credenciais válidas, pedimos para o usuário logar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(caminho_credenciais):
                raise FileNotFoundError(
                    "\nARQUIVO 'credentials.json' NAO ENCONTRADO!\n"
                    "Voce precisa baixar o arquivo do Google Cloud e coloca-lo "
                    "na mesma pasta do main.py com o nome 'credentials.json'."
                )
            
            # Isso vai abrir uma janela no seu navegador pedindo pra logar
            flow = InstalledAppFlow.from_client_secrets_file(caminho_credenciais, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Salva o token para não ter que fazer login de novo na próxima vez
        with open(caminho_token, 'w') as token:
            token.write(creds.to_json())
            
    return creds
