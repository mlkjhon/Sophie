"""
agenda_tool.py — Permite que a Sophie veja compromissos na sua Agenda.
"""
from googleapiclient.discovery import build
import datetime

try:
    from ferramentas.google_auth import obter_credenciais
except ImportError:
    from google_auth import obter_credenciais

def listar_proximos_eventos(max_resultados: int = 5):
    """
    Lista os próximos eventos da sua agenda.
    """
    print("📅 [Calendar] Buscando próximos compromissos...")
    try:
        creds = obter_credenciais()
        servico = build('calendar', 'v3', credentials=creds)
        
        # Pega a data e hora de agora no formato que o Google entende
        agora = datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')
        
        # Busca os eventos
        eventos_resultado = servico.events().list(
            calendarId='primary', timeMin=agora,
            maxResults=max_resultados, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        eventos = eventos_resultado.get('items', [])
        
        if not eventos:
            return "Nenhum compromisso marcado para os próximos dias."
            
        resumo = "Seus próximos eventos:\n"
        for evento in eventos:
            # Pega o horário (se tiver) ou a data (se for evento de dia inteiro)
            inicio = evento['start'].get('dateTime', evento['start'].get('date'))
            resumo += f"- {inicio}: {evento['summary']}\n"
            
        return resumo
    except Exception as e:
        return f"❌ Erro ao acessar o Google Calendar: {e}"

def criar_evento_agenda(assunto: str, inicio: str, fim: str):
    """
    Cria um compromisso na agenda.
    Obrigatório passar no formato ISO, ex: 2026-06-01T21:00:00-03:00
    """
    print(f"📅 [Calendar] Tentando criar evento: {assunto} de {inicio} até {fim}")
    try:
        creds = obter_credenciais()
        servico = build('calendar', 'v3', credentials=creds)
        
        evento = {
          'summary': assunto,
          'start': {
            'dateTime': inicio,
            'timeZone': 'America/Sao_Paulo',
          },
          'end': {
            'dateTime': fim,
            'timeZone': 'America/Sao_Paulo',
          },
        }

        evento_criado = servico.events().insert(calendarId='primary', body=evento).execute()
        return f"✅ Evento criado com sucesso! Link: {evento_criado.get('htmlLink')}"
    except Exception as e:
        return f"❌ Erro ao criar evento no Google Calendar: {e}"

if __name__ == "__main__":
    print("="*40)
    print("Testando Ferramenta: Google Agenda")
    print("="*40)
    print(listar_proximos_eventos())
