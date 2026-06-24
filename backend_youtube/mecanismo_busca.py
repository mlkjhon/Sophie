import requests  # Importa a biblioteca para fazer requisições e conexões de internet
import webbrowser  # Importa a biblioteca do sistema operacional para abrir o navegador de internet
import sys  # Importa ferramentas básicas do sistema para controle do encerramento do programa

# Força o terminal a aceitar caracteres especiais (emojis, etc) para evitar erros no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# CONFIGURAÇÃO: CONFIGURA SUA CHAVE AQUI
# ==========================================
# Substitua o texto abaixo pelas letras e números da chave que você copiou no Passo 1.
CHAVE_DA_API = "AIzaSyC2Uj4_r8-S_Jt2VrHKTCFA0kIxxK6HyVA"

def buscar_videos_no_youtube(termo_da_busca, token_da_pagina=""):
    """
    Função principal de backend. Ela se conecta ao YouTube, faz a busca,
    controla as páginas (avançar/voltar) e trata erros do servidor.
    """
    # Este é o endereço web oficial (Endpoint) que o Google disponibiliza para buscas
    url_do_servidor = "https://www.googleapis.com/youtube/v3/search"
    
    # Montamos o dicionário com todas as regras e filtros que o YouTube exige na busca
    parametros_da_requisicao = {
        "part": "snippet",            # Solicita os dados textuais básicos do vídeo (título, canal, etc)
        "q": termo_da_busca,          # Passa a palavra de busca que o usuário digitou
        "type": "video",              # Trava a busca para trazer APENAS vídeos (ignora canais ou playlists)
        "maxResults": 5,              # Define que queremos receber apenas 5 vídeos por página para não sobrecarregar
        "pageToken": token_da_pagina, # Envia o código da página atual. Se estiver vazio, traz a primeira página
        "key": CHAVE_DA_API,          # Envia a nossa chave de segurança para validar o acesso
        "videoDuration": "medium",    # Filtra vídeos com mais de 4 minutos, cortando conteúdos rasos e shorts
        "relevanceLanguage": "pt",    # Prioriza vídeos em português
        "order": "relevance"          # Garante que os mais relevantes e bem avaliados venham primeiro
    }
    
    try:
        # Dispara uma chamada HTTP GET real para os servidores do Google levando nossos parâmetros
        resposta_bruta = requests.get(url_do_servidor, params=parametros_da_requisicao, timeout=10)
        
        # Verifica o status da resposta. Se o servidor do Google retornou erro (400, 403, 500), joga direto para o bloco Except
        resposta_bruta.raise_for_status()
        
        # Converte o bloco de texto bruto recebido do Google em um formato JSON mapeado (Dicionário Python)
        dados_convertidos = resposta_bruta.json()
        
        # Se a estrutura 'items' estiver vazia, significa que a busca funcionou mas o termo não gerou resultados
        if not dados_convertidos.get("items"):
            print("\n[AVISO]: Nenhum vídeo foi localizado com esse termo de busca.")
            return None
            
        # Cria uma lista limpa na memória para guardarmos apenas os dados que nos interessam
        lista_de_videos_filtrada = []
        
        # Coleta os tokens secretos de paginação. Se não existirem (ex: última página), devolve um texto vazio ""
        proxima_pagina = dados_convertidos.get("nextPageToken", "")
        pagina_anterior = dados_convertidos.get("prevPageToken", "")
        
        # Entra em um loop (laço de repetição) para ler um vídeo por vez de dentro da lista que o Google mandou
        for item in dados_convertidos["items"]:
            id_unico_do_video = item["id"]["videoId"]  # Captura a identificação alfa-numérica do vídeo
            titulo_do_video = item["snippet"]["title"]  # Captura o título real do vídeo no YouTube
            nome_do_canal = item["snippet"]["channelTitle"]  # Captura o nome do canal que publicou o vídeo
            
            # Concatena a string padrão global de links do YouTube com o ID do vídeo para gerar a URL exata de abertura
            url_absoluta_reproducao = f"https://www.youtube.com/watch?v={id_unico_do_video}"
            
            # Cria um objeto estruturado e limpo para o vídeo atual
            estrutura_do_video = {
                "id": id_unico_do_video,
                "titulo": titulo_do_video,
                "canal": nome_do_canal,
                "link": url_absoluta_reproducao
            }
            
            # Adiciona esse objeto final dentro da nossa lista de armazenamento
            lista_de_videos_filtrada.append(estrutura_do_video)
            
        # Devolve para quem chamou a função um pacote contendo a lista dos 5 vídeos e os controles de página
        return {
            "lista_videos": lista_de_videos_filtrada,
            "token_proxima": proxima_pagina,
            "token_anterior": pagina_anterior
        }
        
    except requests.exceptions.HTTPError as erro_de_protocolo:
        # Se o erro disparado possuir o código de status 403, significa falta de autorização ou cota estourada
        if resposta_bruta.status_code == 403:
            print("\n[ERRO CRÍTICO 403]: Sua cota diária gratuita acabou ou a API do YouTube está desativada no seu painel.")
        # Se o código for 400, indica parâmetros errados, quase sempre por conta da chave digitada incorretamente
        elif resposta_bruta.status_code == 400:
            print("\n[ERRO CRÍTICO 400]: Sua Chave de API inserida no código está incorreta, inválida ou com caracteres faltando.")
        else:
            print(f"\n[ERRO DE SERVIDOR]: Falha na comunicação com o servidor do YouTube. Detalhes: {erro_de_protocolo}")
        return None
        
    except requests.exceptions.ConnectionError:
        # Esse bloco é ativado se o computador rodando o código não conseguir estabelecer sinal com a rede externa
        print("\n[ERRO DE REDE]: Não foi possível detectar conexão ativa com a internet. Verifique seu cabo ou Wi-Fi.")
        return None
        
    except Exception as erro_desconhecido:
        # Captura qualquer outra falha genérica de sistema para evitar que o programa trave e feche abruptamente
        print(f"\n[ERRO INESPERADO]: Algo deu errado na execução interna da lógica: {erro_desconhecido}")
        return None

def disparar_abertura_do_video(url_alvo):
    """
    Função de execução de sistema operacional. Ela recebe a URL gerada e força
    o hardware do servidor/máquina a abrir a tela de exibição nativa.
    """
    print(f"\n[SISTEMA]: Enviando comando de hardware... Abrindo link: {url_alvo}")
    # O método open invoca o navegador padrão configurado no sistema operacional do usuário e abre a URL
    webbrowser.open(url_alvo)

# ==========================================
# ROTINA INTERATIVA DE TESTE (SIMULADOR DO BACKEND)
# ==========================================
# Este bloco abaixo simula um terminal interativo para você testar a lógica pura funcionando na prática.
if __name__ == "__main__":
    print("=== BACKEND DO YOUTUBE INICIADO COM SUCESSO ===")
    
    # Solicita que o usuário digite um termo de busca inicial pelo teclado do terminal
    termo_usuario = input("Digite o que deseja pesquisar no YouTube: ")
    
    token_atual = ""       # Inicializa o controle de página como vazio (página 1)
    historico_tokens = []  # Cria um histórico de páginas para podermos rastrear o comando de "voltar"
    
    # Entra em um loop infinito de navegação do sistema, que só para se o usuário pedir para sair
    while True:
        # Executa a nossa função de busca passando o termo e o token da página em que estamos
        resultado_da_busca = buscar_videos_no_youtube(termo_usuario, token_atual)
        
        # Se a busca retornou falha (por erros de chave, conexão, etc), encerra o loop de testes
        if not resultado_da_busca:
            print("[SISTEMA]: Encerrando o programa devido a falhas críticas.")
            sys.exit()
            
        videos = resultado_da_busca["lista_videos"]
        proximo = resultado_da_busca["token_proxima"]
        anterior = resultado_da_busca["token_anterior"]
        
        print(f"\n--- RESULTADOS DA BUSCA PARA: '{termo_usuario}' ---")
        # Exibe os 5 vídeos encontrados na tela do terminal, numerados de 1 a 5
        for indice, video in enumerate(videos, start=1):
            print(f"[{indice}] Título: {video['titulo']}")
            print(f"    Canal: {video['canal']}")
            print(f"    Link gerado pelo backend: {video['link']}\n")
            
        print("=== OPÇÕES DE NAVEGAÇÃO E EXECUÇÃO ===")
        print("De [1] a [5] -> Escolha o número do vídeo para abrir e assistir")
        if proximo:
            print("   [P]       -> Avançar para a Próxima Página de resultados")
        if anterior:
            print("   [V]       -> Voltar para a Página Anterior de resultados")
        print("   [N]       -> Fazer uma Nova Busca com outro termo")
        print("   [S]       -> Sair do sistema")
        
        # Coleta o comando de decisão digitado pelo usuário no terminal
        opcao = input("\nDigite sua opção: ").strip().upper()
        
        # Verifica se o usuário digitou um número válido entre 1 e o total de vídeos listados
        if opcao.isdigit() and 1 <= int(opcao) <= len(videos):
            video_escolhido = videos[int(opcao) - 1]  # Subtrai 1 porque listas em programação começam no índice 0
            disparar_abertura_do_video(video_escolhido["link"])  # Executa o comando de abertura do vídeo escolhido
            
        elif opcao == "P" and proximo:
            # Para avançar, salvamos o token da página atual no histórico de retorno e atualizamos o token com o avançar
            historico_tokens.append(token_atual)
            token_atual = proximo
            print("\n[SISTEMA]: Carregando próxima página do backend...")
            
        elif opcao == "V" and anterior:
            # Para voltar, removemos o último token registrado do nosso histórico e voltamos para ele
            if historico_tokens:
                token_atual = historico_tokens.pop()
            else:
                token_atual = ""
            print("\n[SISTEMA]: Retornando página no backend...")
            
        elif opcao == "N":
            # Reseta os controles de paginação e solicita um novo termo de pesquisa
            termo_usuario = input("\nDigite o novo termo que deseja pesquisar: ")
            token_atual = ""
            historico_tokens = []
            
        elif opcao == "S":
            # Quebra o laço de repetição infinito e fecha o programa com sucesso
            print("\n[SISTEMA]: Desconectando dos serviços do YouTube. Até logo!")
            break
        else:
            print("\n[AVISO]: Opção inválida ou navegação indisponível. Preste atenção no menu.")
