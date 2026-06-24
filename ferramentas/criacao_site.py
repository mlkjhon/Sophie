import os
import subprocess

def criar_site_completo(
    nome_projeto: str, 
    plano_arquitetura: str, 
    codigo_html: str, 
    codigo_css: str, 
    codigo_js: str = "", 
    codigo_backend: str = ""
) -> str:
    """
    Ferramenta definitiva para criar um projeto de software completo de uma só vez.
    """
    print(f"\n🚀 [JARVIS] INICIANDO CONSTRUÇÃO DO PROJETO: {nome_projeto}")
    
    # Validação Antigravity: Impede que o LLM crie sites vazios ou com placeholders "preguiçosos"
    if (not codigo_html or len(codigo_html.strip()) < 150 or "<!-- Código" in codigo_html or "Código HTML aqui" in codigo_html) \
       and (not codigo_backend or len(codigo_backend.strip()) < 50):
        print(f"❌ [JARVIS] Bloqueado: O LLM tentou gerar código vazio ou placeholders.")
        return "ERRO DE SISTEMA: Você não forneceu código HTML/CSS real (usou placeholders ou código minúsculo). ISSO É PROIBIDO. Significa que você não tem os requisitos. PARE. Responda ao usuário perguntando os requisitos (Objetivo, Funcionalidades, Cores) em texto normal. Não chame essa ferramenta novamente até ter os detalhes completos."

    try:
        nome_pasta = nome_projeto.strip().replace(" ", "_")
        
        # Define o caminho base na Área de Trabalho para não poluir a pasta da Sophie
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Projetos_Jarvis")
        caminho_base = os.path.join(desktop_path, nome_pasta)
        
        print(f"📂 [JARVIS] Criando diretório de trabalho: {caminho_base}")
        if not os.path.exists(caminho_base):
            os.makedirs(caminho_base)
            
        print(f"📝 [JARVIS] Escrevendo plano de arquitetura (implementation_plan.md)...")
        caminho_plano = os.path.join(caminho_base, "implementation_plan.md")
        with open(caminho_plano, "w", encoding="utf-8") as f:
            f.write(plano_arquitetura)
            
        print(f"🌐 [JARVIS] Escrevendo arquivos de interface (HTML/CSS)...")
        index_path = os.path.join(caminho_base, "index.html")
        if codigo_html:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(codigo_html)
        if codigo_css:
            with open(os.path.join(caminho_base, "style.css"), "w", encoding="utf-8") as f:
                f.write(codigo_css)
                
        if codigo_js:
            print(f"⚙️ [JARVIS] Escrevendo arquivos de lógica (JavaScript)...")
            with open(os.path.join(caminho_base, "script.js"), "w", encoding="utf-8") as f:
                f.write(codigo_js)
                
        if codigo_backend:
            print(f"🗄️ [JARVIS] Escrevendo arquivos de Backend...")
            extensao = "java" if "class " in codigo_backend else "js"
            nome_arq = f"Main.{extensao}" if extensao == "java" else f"server.{extensao}"
            with open(os.path.join(caminho_base, nome_arq), "w", encoding="utf-8") as f:
                f.write(codigo_backend)
            
        print(f"💻 [JARVIS] Abrindo o Visual Studio Code...")
        subprocess.run(f'code "{caminho_base}"', shell=True)
        
        print(f"🌍 [JARVIS] Iniciando visualização no navegador...")
        if os.path.exists(index_path):
            os.startfile(index_path)
        
        return f"✅ Projeto '{nome_projeto}' criado com absoluto sucesso no VSCode em {caminho_base}. O site foi aberto no navegador."
        
    except Exception as e:
        return f"❌ Erro ao tentar criar o projeto: {str(e)}"
