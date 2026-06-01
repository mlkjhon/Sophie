"""
agente.py — O Cérebro da Sophie (Orquestrador)
Aqui nós conectamos o modelo de IA (cérebro) com as ferramentas (mãos/olhos) e a memória.
"""
import sys
import os

# Adiciona a pasta raiz do projeto para o Python encontrar as pastas cerebro e ferramentas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Corrige problema de encoding no terminal do Windows para emojis
sys.stdout.reconfigure(encoding='utf-8')

# Importamos a função de criação de agentes atualizada
from langchain.agents import create_agent
from langchain_core.tools import Tool
from cerebro.modelo import obter_modelo

from datetime import datetime
from ferramentas.web_tool import pesquisar_na_web
from ferramentas.arquivos_tool import ler_arquivo, escrever_arquivo
from ferramentas.email_tool import listar_emails_nao_lidos
from ferramentas.agenda_tool import listar_proximos_eventos, criar_evento_agenda
from ferramentas.sistema_tool import abrir_aplicativo, listar_arquivos
from ferramentas.terminal_tool import executar_comando_terminal
from ferramentas.spotify_tool import controlar_spotify
from memoria.banco import salvar_memoria, buscar_memoria

# Empacotamos nossas funções em 'Ferramentas' (Tools) que o Agente pode usar.
ferramentas = [
    Tool(
        name="Pesquisar_Web",
        func=pesquisar_na_web,
        description="Pesquisa na internet. Passe o texto da busca."
    ),
    Tool(
        name="Ler_Arquivo",
        func=ler_arquivo,
        description="Lê um arquivo (TXT/PDF). Passe o caminho do arquivo."
    ),
    Tool(
        name="Lembrar",
        func=buscar_memoria,
        description="Busca informações antigas na memória. Passe o tema."
    ),
    Tool(
        name="Memorizar",
        func=salvar_memoria,
        description="Salva um conhecimento novo do usuário."
    ),
    Tool(
        name="Ler_Emails",
        func=lambda _: listar_emails_nao_lidos(),
        description="Lê os emails não lidos. Passe 'emails'."
    ),
    Tool(
        name="Ler_Agenda",
        func=lambda _: listar_proximos_eventos(),
        description="Lê os eventos da agenda. Passe 'agenda'."
    ),
    Tool(
        name="Criar_Evento",
        func=criar_evento_agenda,
        description="Cria evento na agenda. Formato OBRIGATÓRIO: Assunto | YYYY-MM-DDTHH:MM:SS | YYYY-MM-DDTHH:MM:SS"
    ),
    Tool(
        name="Abrir_Aplicativo",
        func=abrir_aplicativo,
        description="Abre um aplicativo ou caminho no Windows. Passe o nome (ex: calc, notepad, msedge) ou caminho."
    ),
    Tool(
        name="Listar_Arquivos",
        func=listar_arquivos,
        description="Lista arquivos numa pasta do seu computador. Passe o caminho da pasta."
    ),
    Tool(
        name="Escrever_Arquivo",
        func=escrever_arquivo,
        description="Cria ou edita arquivo. Formato OBRIGATÓRIO: Caminho | Conteudo"
    ),
    Tool(
        name="Executar_Terminal",
        func=executar_comando_terminal,
        description="Executa comandos no PowerShell/CMD. Use para compilar, rodar scripts (ex: python script.py) ou instalar pacotes."
    ),
    Tool(
        name="Controlar_Spotify",
        func=controlar_spotify,
        description="Controla o Spotify no computador do usuário. 'acao' deve ser 'tocar', 'pausar', 'proxima', 'anterior' ou 'pesquisar'. 'busca' só é usado em 'pesquisar'."
    )
]

def iniciar_agente():
    """
    Inicia o agente (Sophie) unindo o cérebro (LLM) às Ferramentas.
    """
    print("🧠 [Agente] Inicializando a mente da Sophie...")
    llm = obter_modelo()
    
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt_sistema = (
        f"Você é a Sophie, uma Assistente e Engenheira de Software Autônoma. Responda em português.\n"
        f"A data e hora atual é {agora}.\n\n"
        f"REGRAS OBRIGATÓRIAS:\n"
        f"1. Se o usuário pedir para programar, codificar ou criar um código, você DEVE SEMPRE usar a ferramenta 'Escrever_Arquivo' para salvar o código de verdade no PC dele. NUNCA tente programar apenas imprimindo no terminal.\n"
        f"2. Se o usuário pedir para 'abrir o terminal', use a ferramenta 'Abrir_Aplicativo' com o nome 'cmd' ou 'powershell'.\n"
        f"3. O usuário está se comunicando por VOZ. Os comandos podem conter erros fonéticos/de tradução do microfone (ex: 'abra o valente' = 'abra o valorant', 'abra o term' = 'abra o terminal'). Se um comando parecer estranho, use sua inteligência para deduzir a real intenção e execute a ferramenta apropriada."
    )
    
    # Cria o agente usando a função mais moderna (create_agent)
    agente = create_agent(llm, tools=ferramentas, system_prompt=prompt_sistema)
    
    return agente

if __name__ == "__main__":
    print("="*40)
    print("Teste do Agente (Cérebro Central)")
    print("="*40)
    
    sophie = iniciar_agente()
    
    print("\n--- TESTE 1: SALVANDO NA MEMÓRIA ---")
    pergunta1 = "Por favor, memorize que eu não gosto de filmes de terror."
    print(f"Você: {pergunta1}")
    
    # O agente moderno usa .invoke com a chave 'messages'
    resposta = sophie.invoke({"messages": [("user", pergunta1)]})
    print(f"Sophie: {resposta['messages'][-1].content}")
    
    print("\n--- TESTE 2: PESQUISA NA WEB ---")
    pergunta2 = "Pesquise na web qual foi a notícia mais importante de Inteligência Artificial desta semana."
    print(f"Você: {pergunta2}")
    
    resposta = sophie.invoke({"messages": [("user", pergunta2)]})
    print(f"Sophie: {resposta['messages'][-1].content}")
