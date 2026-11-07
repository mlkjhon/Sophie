"""
web_tool.py — Dá à Sophie o poder de pesquisar na internet.
Usa o DuckDuckGo (gratuito) para buscar informações em tempo real
sem precisar de chaves de API pagas.
"""

from ddgs import DDGS

def pesquisar_na_web(pergunta: str, max_resultados: int = 3) -> str:
    """
    Pesquisa uma pergunta na internet e retorna um resumo dos resultados.
    
    Args:
        pergunta: O que você quer pesquisar (ex: "Clima hoje em SP")
        max_resultados: Quantos sites ele deve checar (padrão 3)
        
    Returns:
        Um texto contendo os resumos dos sites encontrados.
    """
    print(f"[Pesquisando na Web] '{pergunta}'...")

    try:
        # Inicializa o buscador do DuckDuckGo
        buscador = DDGS()

        # Faz a pesquisa pedindo textos
        resultados = buscador.text(pergunta, max_results=max_resultados)

        if not resultados:
            return "Nenhum resultado encontrado na web."

        # Junta os resultados em um único texto para a Sophie ler depois
        texto_final = "Resultados da pesquisa:\n\n"
        for i, res in enumerate(resultados, 1):
            titulo = res.get('title', 'Sem titulo')
            conteudo = res.get('body', 'Sem conteudo')
            link = res.get('href', 'Sem link')
            texto_final += f"{i}. {titulo}\n   {conteudo}\n   Fonte: {link}\n\n"

        return texto_final

    except Exception as e:
        erro = f"Erro ao pesquisar na internet: {str(e)}"
        print(erro)
        return erro

if __name__ == "__main__":
    # Teste para ver se a ferramenta consegue acessar a internet
    print("=" * 40)
    print("Testando Ferramenta: Pesquisa Web")
    print("=" * 40)
    
    resultado = pesquisar_na_web("Quais são as últimas notícias sobre Inteligência Artificial?", max_resultados=2)
    print("\nO que a ferramenta encontrou:\n")
    print(resultado)
