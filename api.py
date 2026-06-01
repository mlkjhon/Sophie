"""
api.py — A "Boca e os Ouvidos" da Sophie.
Cria um servidor local com FastAPI para podermos conversar com a Sophie via web ou conectar em qualquer outro aplicativo no futuro.
"""
from fastapi import FastAPI
from pydantic import BaseModel

# Importamos o cérebro que acabamos de testar
from cerebro.agente import iniciar_agente

# Inicializamos o aplicativo FastAPI (isso cria o nosso servidor web)
app = FastAPI(
    title="Sophie Assistant API",
    description="A API privada do seu assistente inteligente rodando localmente.",
    version="1.0"
)

# Inicializamos a mente da Sophie assim que a API começar a rodar
print("⏳ Carregando a mente da Sophie para a API...")
sophie = iniciar_agente()
print("✅ Sophie está conectada e pronta para conversar!")

# Aqui criamos o "Molde" do que a nossa API espera receber do usuário
class MensagemUsuario(BaseModel):
    texto: str

# E o "Molde" do que ela vai devolver
class RespostaSophie(BaseModel):
    resposta: str

# Esta é a nossa rota principal. 
# Sempre que alguém mandar um "POST" para http://localhost:8000/chat, essa função roda.
@app.post("/chat", response_model=RespostaSophie)
def conversar(dados: MensagemUsuario):
    """
    Envia um texto para a Sophie pensar e devolve a resposta final dela.
    """
    print(f"\n👤 Você: {dados.texto}")
    
    # Mandamos a mensagem pro agente resolver e processar as ferramentas se precisar
    resultado = sophie.invoke({"messages": [("user", dados.texto)]})
    
    # A resposta final fica na última mensagem da lista de resultados
    texto_resposta = resultado['messages'][-1].content
    
    print(f"🤖 Sophie: {texto_resposta}")
    return {"resposta": texto_resposta}

@app.get("/")
def home():
    """Rota inicial só para confirmar que está tudo no ar."""
    return {"status": "Sophie está Online!", "dica": "Acesse http://localhost:8000/docs para conversar com ela."}
