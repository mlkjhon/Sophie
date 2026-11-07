"""
api.py — A "Boca e os Ouvidos" da Sophie.
Servidor local FastAPI (sem auth, sem usuários, um único agente Sophie).
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from cerebro.agente import iniciar_agente
from dados.db import get_db, iniciar_banco
from dados.models import Conversation, Message

# Inicializamos as tabelas no DB caso não existam
iniciar_banco()

app = FastAPI(
    title="Sophie Assistant API",
    description="A API do seu assistente inteligente rodando localmente.",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Um único agente Sophie (lazy-loaded) ───
_sophie_agent = None

def get_sophie():
    """Retorna o agente Sophie, criando na primeira chamada (lazy)."""
    global _sophie_agent
    if _sophie_agent is None:
        print("[API] Inicializando agente único da Sophie...")
        _sophie_agent = iniciar_agente()
        print("Sophie pronta!")
    return _sophie_agent


# --- SCHEMAS ---
class MensagemUsuario(BaseModel):
    texto: str
    conversation_id: Optional[int] = None

class RespostaSophie(BaseModel):
    resposta: str
    conversation_id: int


# --- ROTAS DO CHAT / HISTÓRICO ---

@app.get("/chat/history")
def listar_conversas(db: Session = Depends(get_db)):
    conversas = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(30).all()
    return [{"id": c.id, "title": c.title, "created_at": str(c.created_at)} for c in conversas]


@app.get("/chat/{conversation_id}/messages")
def listar_mensagens(conversation_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return [{"sender": m.sender, "text": m.text, "created_at": str(m.created_at)} for m in msgs]


@app.delete("/chat/{conversation_id}")
def deletar_conversa(conversation_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    db.delete(conversa)
    db.commit()
    return {"status": "deletado"}


@app.post("/chat", response_model=RespostaSophie)
def conversar(dados: MensagemUsuario, db: Session = Depends(get_db)):
    print(f"\nVoce: {dados.texto}")

    # Buscar ou criar conversa
    if dados.conversation_id:
        conversa = db.query(Conversation).filter(Conversation.id == dados.conversation_id).first()
    else:
        conversa = None

    if not conversa:
        # Auto-gera título da conversa com as primeiras palavras
        titulo = dados.texto[:50].strip()
        if len(dados.texto) > 50:
            titulo += "..."
        conversa = Conversation(title=titulo)
        db.add(conversa)
        db.commit()
        db.refresh(conversa)

    # Salvar mensagem do usuário
    msg_usuario = Message(conversation_id=conversa.id, sender="user", text=dados.texto)
    db.add(msg_usuario)
    db.commit()

    # Chamar o agente único Sophie
    sophie = get_sophie()
    resultado = sophie.invoke({"messages": [("user", dados.texto)]})

    texto_resposta = resultado['messages'][-1].content

    # Salvar resposta da Sophie
    msg_sophie = Message(conversation_id=conversa.id, sender="sophie", text=texto_resposta)
    db.add(msg_sophie)
    db.commit()

    print(f"Sophie: {texto_resposta}")
    return {"resposta": texto_resposta, "conversation_id": conversa.id}


@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
