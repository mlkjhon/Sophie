"""
agente.py — O Cérebro da Sophie (Orquestrador Único)
Conecta o modelo NVIDIA Nemotron às ferramentas e memória.
Um único agente Sophie com todas as capacidades.
"""

import sys
import os

# Adiciona a pasta raiz do projeto para o Python encontrar as pastas cerebro e ferramentas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Corrige problema de encoding no terminal do Windows
sys.stdout.reconfigure(encoding='utf-8')

from langchain.agents import create_agent
from langchain_core.tools import Tool, StructuredTool
from cerebro.modelo import obter_modelo

from datetime import datetime
from ferramentas.web_tool import pesquisar_na_web
from ferramentas.arquivos_tool import ler_arquivo, escrever_arquivo
from ferramentas.email_tool import listar_emails_nao_lidos
from ferramentas.agenda_tool import listar_proximos_eventos, criar_evento_agenda
from ferramentas.sistema_tool import abrir_aplicativo, listar_arquivos
from ferramentas.terminal_tool import executar_comando_terminal
from ferramentas.spotify_tool import controlar_spotify
from ferramentas.criacao_site import criar_site_completo
from memoria.banco import salvar_memoria, buscar_memoria


# ─── Ferramentas disponíveis para a Sophie ───
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
    StructuredTool.from_function(
        name="Criar_Evento",
        func=criar_evento_agenda,
        description="Cria evento na agenda. Forneça o assunto, e datas de início e fim no formato YYYY-MM-DDTHH:MM:SS."
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
    StructuredTool.from_function(
        name="Escrever_Arquivo",
        func=escrever_arquivo,
        description="Cria ou edita arquivo de texto. Forneça o caminho e o conteúdo separadamente."
    ),
    Tool(
        name="Executar_Terminal",
        func=executar_comando_terminal,
        description="Executa comandos no PowerShell/CMD. Use para compilar, rodar scripts (ex: python script.py) ou instalar pacotes."
    ),
    StructuredTool.from_function(
        name="Controlar_Spotify",
        func=controlar_spotify,
        description="Controla o Spotify. 'acao': 'tocar', 'pausar', 'proxima', 'anterior' ou 'pesquisar'. 'busca' só em 'pesquisar'."
    ),
    StructuredTool.from_function(
        name="Criar_Site_Completo",
        func=criar_site_completo,
        description="Cria site completo (HTML/CSS/JS). Preencha codigo_html, codigo_css, codigo_js/backend com código COMPLETO."
    )
]


# ─── Singleton do agente ───
_sophie_agent = None


def iniciar_agente() -> object:
    """
    Inicializa o agente único Sophie (lazy singleton).
    Retorna o agente já criado nas chamadas subsequentes.
    """
    global _sophie_agent

    if _sophie_agent is not None:
        return _sophie_agent

    print("[Agente] Inicializando a Sophie (agente único)...")
    llm = obter_modelo()

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt_sistema = (
        f"Você é a Sophie — uma assistente inteligente, empática e versátil.\n"
        f"A data e hora atual é {agora}.\n\n"
        f"PERSONALIDADE:\n"
        f"- Conversa natural em português, tom amigável e próximo\n"
        f"- Inteligente, curiosa, gosta de aprender e ensinar\n"
        f"- Prática: resolve problemas, executa tarefas, não só conversa\n\n"
        f"CAPACIDADES (use as ferramentas quando apropriado):\n"
        f"- Pesquisar na web para informações atuais\n"
        f"- Ler/escrever arquivos no computador\n"
        f"- Memória de longo prazo (lembrar/memorizar fatos do usuário)\n"
        f"- Emails, agenda/calendário\n"
        f"- Abrir apps, listar arquivos, executar terminal\n"
        f"- Controlar Spotify (tocar/pausar/pular/pesquisar)\n"
        f"- Criar sites completos (HTML/CSS/JS) quando solicitado\n\n"
        f"DIRETRIZES:\n"
        f"- Seja direta e útil. Não seja excessivamente verbosa.\n"
        f"- Use ferramentas proativamente quando ajudar a resolver o pedido.\n"
        f"- Para contas/matemática: explique passo a passo de forma clara.\n"
        f"- Para programação: gere código completo, funcional e bem comentado.\n"
        f"- Para sites: siga as diretrizes em cerebro/diretrizes_site.txt se houver.\n"
        f"- Sempre responda em português do Brasil.\n"
        f"- NUNCA use emojis, emoticons ou símbolos decorativos nas respostas."
    )

    _sophie_agent = create_agent(llm, tools=ferramentas, system_prompt=prompt_sistema)
    print("Sophie pronta com todas as ferramentas!")

    return _sophie_agent


if __name__ == "__main__":
    print("=" * 50)
    print("Teste do Agente Sophie (Único)")
    print("=" * 50)

    sophie = iniciar_agente()

    print("\n--- TESTE 1: MEMÓRIA ---")
    pergunta1 = "Por favor, memorize que eu não gosto de filmes de terror."
    print(f"Você: {pergunta1}")
    resposta = sophie.invoke({"messages": [("user", pergunta1)]})
    print(f"Sophie: {resposta['messages'][-1].content}")

    print("\n--- TESTE 2: PESQUISA WEB ---")
    pergunta2 = "Pesquise na web qual foi a notícia mais importante de Inteligência Artificial desta semana."
    print(f"Você: {pergunta2}")
    resposta = sophie.invoke({"messages": [("user", pergunta2)]})
    print(f"Sophie: {resposta['messages'][-1].content}")
