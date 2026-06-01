"""
email_tool.py — Permite ler e enviar emails usando sua conta do Gmail.
"""
from googleapiclient.discovery import build
import os

# Tenta importar da mesma pasta ou do projeto principal
try:
    from ferramentas.google_auth import obter_credenciais
except ImportError:
    from google_auth import obter_credenciais

def listar_emails_nao_lidos(max_resultados: int = 5):
    """
    Lista os últimos emails não lidos da sua caixa de entrada.
    """
    print("📧 [Gmail] Buscando emails não lidos...")
    try:
        creds = obter_credenciais()
        servico = build('gmail', 'v1', credentials=creds)
        
        # Pede apenas emails na Caixa de Entrada ('INBOX') que estão não lidos ('UNREAD')
        resultados = servico.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_resultados).execute()
        mensagens = resultados.get('messages', [])
        
        if not mensagens:
            return "Você não tem nenhum email não lido! 🎉"
            
        resumo = "Seus emails não lidos:\n"
        for msg in mensagens:
            # Pega o assunto e o remente de cada email
            txt_msg = servico.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            cabecalhos = txt_msg.get('payload', {}).get('headers', [])
            
            assunto = "Sem Assunto"
            remetente = "Desconhecido"
            for header in cabecalhos:
                if header['name'] == 'Subject':
                    assunto = header['value']
                if header['name'] == 'From':
                    remetente = header['value']
                    
            resumo += f"- De: {remetente} | Assunto: {assunto}\n"
            
        return resumo
    except Exception as e:
        return f"❌ Erro ao acessar o Gmail: {e}"

if __name__ == "__main__":
    print("="*40)
    print("Testando Ferramenta: Gmail")
    print("="*40)
    print(listar_emails_nao_lidos())
