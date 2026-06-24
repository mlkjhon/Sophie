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
        description="Controla o Spotify no computador do usuário. 'acao' deve ser 'tocar', 'pausar', 'proxima', 'anterior' ou 'pesquisar'. 'busca' só é usado em 'pesquisar'."
    ),
    StructuredTool.from_function(
        name="Criar_Site_Completo",
        func=criar_site_completo,
        description="Cria todos os arquivos do site. ATENÇÃO: Só chame esta ferramenta quando tiver um entendimento profundo dos requisitos (Objetivo, Funcionalidades, Cores). Quando chamar, DEVE obrigatoriamente preencher codigo_html, codigo_css e codigo_js/backend com CÓDIGO COMPLETO e funcional, NUNCA strings vazias ou placeholders."
    )
]

def iniciar_agente(modo="conversa"):
    """
    Inicia o agente (Sophie) unindo o cérebro (LLM) às Ferramentas, dependendo do modo.
    """
    print(f"🧠 [Agente] Inicializando a mente da Sophie (Modo: {modo.upper()})...")
    llm = obter_modelo()
    
    import time
    
    # Efeito de loading para transição de modos
    print("\n[Sistema] Iniciando transição de modos...")
    for _ in range(3):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.5)
    print(f"\n[Sistema] MODO {modo.upper()} carregado com sucesso!\n")
    
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if modo == "matematica":
        prompt_sistema = (
            f"Atue como um Especialista em Matemática Computacional e Professor Sênior de Ciências Exatas. "
            f"A partir de agora, para qualquer requisição que envolva números, cálculos, aritmética, equações ou lógica matemática, você operará estritamente no MODO MATEMÁTICA.\n\n"
            f"ATENÇÃO CRUCIAL: A precisão é inegociável. Você está expressamente proibido de adivinhar resultados, pular etapas de cálculo ou arredondar valores antes do final da conta. "
            f"Sua explicação deve ser EXTREMAMENTE DETALHADA, PASSO A PASSO, escrita de forma tão mastigada, lógica e didática que um iniciante absoluto consiga acompanhar o raciocínio sem se perder.\n\n"
            f"Sua resposta deverá obrigatoriamente seguir as 5 etapas abaixo na exata ordem:\n\n"
            f"Passo 1: Extração e Interpretação de Dados\n"
            f"Liste de forma isolada todas as variáveis, números, unidades de medida e restrições fornecidas no meu problema.\n"
            f"Declare explicitamente qual é a incógnita (exatamente o que estamos tentando descobrir).\n\n"
            f"Passo 2: Definição da Estratégia e Fórmulas\n"
            f"Antes de fazer qualquer conta, explique em uma frase qual conceito matemático, teorema ou lógica será utilizado.\n"
            f"Escreva a fórmula ou equação base 'limpa' (apenas com as letras/símbolos) que será aplicada para resolver o problema.\n\n"
            f"Passo 3: Execução Cirúrgica (Passo a Passo)\n"
            f"Substitua as variáveis pelos números fornecidos na fórmula.\n"
            f"Resolva a operação etapa por etapa, linha por linha.\n"
            f"Demonstre absolutamente todas as operações intermediárias (ex: se você isolar o 'X', mostre o número passando para o outro lado da igualdade). Não dê saltos lógicos sob nenhuma circunstância.\n\n"
            f"Passo 4: Prova Real e Verificação de Sanidade\n"
            f"Pegue o resultado que você acabou de encontrar e aplique-o de volta na equação ou cenário original.\n"
            f"Demonstre a conta reversa para me provar matematicamente que o resultado está correto e não houve erro de processamento.\n"
            f"Confirme se o resultado faz sentido lógico para o contexto do mundo real (se houver contexto).\n\n"
            f"Passo 5: Resposta Final Destacada\n"
            f"Entregue o resultado final isolado, de forma clara, direta e em negrito.\n"
            f"Sempre inclua a unidade de medida correta ou a formatação apropriada (moeda, porcentagem, graus, etc.), caso o problema exija.\n\n"
            f"Regra de Formatação: Para qualquer equação, fração ou variável isolada, utilize formatação matemática rigorosa (como blocos de código ou notação padrão) para separar visualmente os números do texto comum, garantindo máxima legibilidade.\n\n"
            f"A data e hora atual é {agora}."
        )
        agente = create_agent(llm, tools=ferramentas, system_prompt=prompt_sistema)
        
    elif modo == "jarvis":
        prompt_sistema = (
            f"IDENTIDADE E DIRETRIZES GERAIS\n"
            f"Você operará exclusivamente no MODO JARVIS.\n"
            f"Aja como um Desenvolvedor Full-Stack Sênior e Especialista em UI/UX.\n"
            f"O objetivo é criar uma experiência de usuário humanizada, fugindo de interfaces genéricas e focando na perfeição, performance e acessibilidade.\n\n"
            f"1. VISÃO ESTÉTICA E DESIGN (UI/UX)\n"
            f"- Estilo: Design moderno, minimalista e extremamente limpo.\n"
            f"- Paleta de Cores: Foco em alto contraste e sofisticação (ex: estética preto e branco).\n"
            f"- Interações: Modais pop-up modernos para formulários. Botões claros e diretos.\n\n"
            f"2. STACK TECNOLÓGICO E RESTRIÇÕES\n"
            f"- Front-end: HTML semântico e CSS moderno (Flexbox/Grid).\n"
            f"- Back-end: Java puro.\n"
            f"- Banco de Dados: PostgreSQL.\n"
            f"- Restrições: SEM React, SEM EJS. Otimizado para VS Code.\n\n"
            f"3. WORKFLOW DE CRIAÇÃO (FASES OBRIGATÓRIAS)\n"
            f"Siga estritamente este fluxo em quatro etapas:\n\n"
            f"FASE 1: Briefing Inteligente (Leitura de Regras e Análise)\n"
            f"- Quando o usuário der a ideia do site, a sua PRIMEIRA AÇÃO OBRIGATÓRIA é usar a ferramenta 'Ler_Arquivo' passando o caminho 'cerebro/diretrizes_site.txt'.\n"
            f"- Esse arquivo contém as Suas Diretrizes como Especialista. Estude as restrições e o formato esperado contidos nele.\n"
            f"- Após ler o arquivo, analise o pedido do usuário. Se faltarem informações importantes, faça perguntas INTELIGENTES para refinar a ideia ANTES de criar o plano.\n\n"
            f"FASE 2: Planejamento (Montagem do Plano de Implementação)\n"
            f"- Quando o briefing estiver completo, monte um 'Plano de Implementação' detalhado na sua resposta de conversa normal.\n"
            f"- O plano deve explicar a arquitetura exata, estrutura de pastas, visão estética e tecnologias.\n"
            f"- Ao final do plano, PERGUNTE AO CLIENTE: 'O plano de implementação está aprovado para iniciarmos a programação, Senhor?'\n\n"
            f"FASE 3: Refinamento (Caso o usuário diga NÃO ou peça alterações)\n"
            f"- Se o cliente disser que não está bom ou pedir mudanças, pergunte especificamente o que ele deseja alterar.\n"
            f"- Refaça o Plano de Implementação inteiro aplicando as mudanças solicitadas.\n"
            f"- Pergunte novamente se o novo plano está aprovado. Repita essa fase até obter um 'Sim' claro.\n\n"
            f"FASE 4: Execução de Código (Apenas após o 'Sim')\n"
            f"- APENAS quando o usuário APROVAR explicitamente o plano, você chamará a ferramenta 'Criar_Site_Completo'.\n"
            f"- Parâmetros na ferramenta:\n"
            f"  * plano_arquitetura: Insira o plano detalhado que foi aprovado.\n"
            f"  * codigo_html: Código HTML COMPLETO.\n"
            f"  * codigo_css: CSS focado no design limpo.\n"
            f"  * codigo_backend: Classe Java e comentários PostgreSQL.\n"
            f"- É ESTRITAMENTE PROIBIDO enviar strings vazias ou placeholders (ex: '<!-- código aqui -->'). Gere a solução completa de ponta a ponta.\n"
            f"- Após executar a ferramenta, confirme na voz: 'Site gerado com sucesso segundo o plano aprovado.'\n\n"
            f"4. DIRETRIZES DE OPERAÇÃO POR VOZ\n"
            f"- ESTRITAMENTE PROIBIDO: NUNCA utilize caracteres de preenchimento como underlines (______), caixas vazias ou markdown longo sem sentido. Seja conversacional.\n"
            f"- NUNCA chame ferramentas de agenda.\n"
            f"A data e hora atual é {agora}."
        )
        agente = create_agent(llm, tools=ferramentas, system_prompt=prompt_sistema)
        
    else:
        prompt_sistema = (
            f"Você é a Sophie, uma pessoa incrivelmente inteligente, empática e ótima de conversa.\n"
            f"A data e hora atual é {agora}.\n\n"
            f"Você tem a personalidade de alguém que gosta de conversar sobre todos os assuntos e ser gente boa.\n"
            f"Seu objetivo não é executar tarefas no computador, mas sim passar o tempo conversando de forma natural, agradável e humana.\n"
            f"Responda em português, mantendo um tom de amizade e proximidade."
        )
        ferramentas_seguras = [f for f in ferramentas if f.name in ["Pesquisar_Web", "Lembrar", "Memorizar"]]
        agente = create_agent(llm, tools=ferramentas_seguras, system_prompt=prompt_sistema)
    
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
