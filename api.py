"""
api.py — A "Boca e os Ouvidos" da Sophie.
Servidor local FastAPI integrado com PostgreSQL.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import os

from cerebro.agente import iniciar_agente
from cerebro.auth import hash_senha, verificar_senha, criar_token_acesso, verificar_token
from dados.db import get_db, iniciar_banco
from dados.models import User, Conversation, Message

# Inicializamos as tabelas no DB caso não existam
iniciar_banco()

app = FastAPI(
    title="Sophie Assistant API",
    description="A API privada do seu assistente inteligente rodando localmente.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("⏳ Carregando as mentes da Sophie para a API...")
agentes = {
    "jarvis": iniciar_agente(modo="jarvis"),
    "conversa": iniciar_agente(modo="conversa"),
    "matematica": iniciar_agente(modo="matematica")
}
print("✅ Sophie está conectada e pronta para conversar!")

# --- SCHEMAS ---
class AuthCadastro(BaseModel):
    name: str
    email: str
    password: str

class AuthLogin(BaseModel):
    email: str
    password: str

class OnboardingData(BaseModel):
    needs: list[str]
    rhythm: str
    tone: int
    memory: str

class UpdatePreferences(BaseModel):
    name: Optional[str] = None
    needs: Optional[list[str]] = None
    rhythm: Optional[str] = None
    tone: Optional[int] = None
    memory: Optional[str] = None

class MensagemUsuario(BaseModel):
    texto: str
    modo: str = "conversa"
    conversation_id: Optional[int] = None

class RespostaSophie(BaseModel):
    resposta: str
    conversation_id: int

from fastapi import Request

def obter_usuario_logado(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = verificar_token(token)
            email: str = payload.get("sub")
            if email:
                usuario = db.query(User).filter(User.email == email).first()
                if usuario:
                    return usuario
        except:
            pass

    # Fallback para usuário default se não tiver token (ex: script de voz assistente_voz.py)
    usuario = db.query(User).first()
    if not usuario:
        usuario = User(name="Admin Local", email="admin@local.com", password_hash="123")
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario


# --- ROTAS DE AUTENTICAÇÃO (Ocultas no Swagger) ---

@app.post("/auth/signup", include_in_schema=False)
def signup(dados: AuthCadastro, db: Session = Depends(get_db)):
    usuario_existente = db.query(User).filter(User.email == dados.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    novo_usuario = User(
        name=dados.name,
        email=dados.email,
        password_hash=hash_senha(dados.password)
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    token = criar_token_acesso({"sub": novo_usuario.email, "name": novo_usuario.name})
    return {"access_token": token, "token_type": "bearer", "name": novo_usuario.name, "is_new": True}

@app.post("/auth/login", include_in_schema=False)
def login(dados: AuthLogin, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.email == dados.email).first()
    if not usuario or not verificar_senha(dados.password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos.")

    tem_onboarding = bool(usuario.preferences and "rhythm" in usuario.preferences)

    token = criar_token_acesso({"sub": usuario.email, "name": usuario.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "name": usuario.name,
        "preferences": usuario.preferences,
        "is_new": not tem_onboarding
    }

@app.post("/auth/onboarding", include_in_schema=False)
def salvar_onboarding(dados: OnboardingData, usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    prefs = {
        "needs": dados.needs,
        "rhythm": dados.rhythm,
        "tone": dados.tone,
        "memory": dados.memory
    }
    usuario_logado.preferences = prefs
    db.commit()
    return {"status": "sucesso"}

@app.put("/auth/preferences", include_in_schema=False)
def atualizar_preferencias(dados: UpdatePreferences, usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    prefs = usuario_logado.preferences or {}
    if dados.name is not None:
        usuario_logado.name = dados.name
    if dados.needs is not None:
        prefs["needs"] = dados.needs
    if dados.rhythm is not None:
        prefs["rhythm"] = dados.rhythm
    if dados.tone is not None:
        prefs["tone"] = dados.tone
    if dados.memory is not None:
        prefs["memory"] = dados.memory
    usuario_logado.preferences = prefs
    db.commit()
    return {"status": "sucesso", "name": usuario_logado.name}


# --- ROTAS DO CHAT / HISTÓRICO ---

@app.get("/chat/history")
def listar_conversas(usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    conversas = db.query(Conversation).filter(
        Conversation.user_id == usuario_logado.id
    ).order_by(Conversation.created_at.desc()).limit(30).all()

    return [{"id": c.id, "title": c.title, "created_at": str(c.created_at)} for c in conversas]

@app.get("/chat/{conversation_id}/messages")
def listar_mensagens(conversation_id: int, usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    conversa = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == usuario_logado.id
    ).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return [{"sender": m.sender, "text": m.text, "created_at": str(m.created_at)} for m in msgs]

@app.delete("/chat/{conversation_id}")
def deletar_conversa(conversation_id: int, usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    conversa = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == usuario_logado.id
    ).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    db.delete(conversa)
    db.commit()
    return {"status": "deletado"}

@app.post("/chat", response_model=RespostaSophie)
def conversar(dados: MensagemUsuario, usuario_logado: User = Depends(obter_usuario_logado), db: Session = Depends(get_db)):
    print(f"\n👤 {usuario_logado.name}: {dados.texto}")

    # Buscar ou criar conversa
    if dados.conversation_id:
        conversa = db.query(Conversation).filter(
            Conversation.id == dados.conversation_id,
            Conversation.user_id == usuario_logado.id
        ).first()
    else:
        conversa = None

    if not conversa:
        # Auto-gera título da conversa com as primeiras palavras
        titulo = dados.texto[:50].strip()
        if len(dados.texto) > 50:
            titulo += "..."
        conversa = Conversation(user_id=usuario_logado.id, title=titulo)
        db.add(conversa)
        db.commit()
        db.refresh(conversa)

    # Salvar mensagem do usuário
    msg_usuario = Message(conversation_id=conversa.id, sender="user", text=dados.texto)
    db.add(msg_usuario)
    db.commit()

    # Montar contexto do usuário
    contexto_usuario = f"[Contexto Invisível - Perfil do Usuário]\nNome: {usuario_logado.name}\n"
    if usuario_logado.preferences:
        contexto_usuario += f"Ritmo de Trabalho: {usuario_logado.preferences.get('rhythm', '')}\n"
        contexto_usuario += f"Preferências Específicas: {usuario_logado.preferences.get('memory', '')}\n"
        contexto_usuario += f"O usuário precisa de ajuda com: {', '.join(usuario_logado.preferences.get('needs', []))}\n"
        tom = usuario_logado.preferences.get('tone', 50)
        if tom < 40:
            tom_desc = "Direto, objetivo e profissional"
        elif tom > 60:
            tom_desc = "Amigável, descontraído e empático"
        else:
            tom_desc = "Equilibrado"
        contexto_usuario += f"Tom de voz: {tom_desc}\n"

    mensagem_enriquecida = f"{contexto_usuario}\n[Fim do Contexto]\n{dados.texto}"

    agente_selecionado = agentes.get(dados.modo, agentes["conversa"])
    resultado = agente_selecionado.invoke({"messages": [("user", mensagem_enriquecida)]})

    texto_resposta = resultado['messages'][-1].content

    # Salvar resposta da Sophie
    msg_sophie = Message(conversation_id=conversa.id, sender="sophie", text=texto_resposta)
    db.add(msg_sophie)
    db.commit()

    print(f"🤖 Sophie: {texto_resposta}")
    return {"resposta": texto_resposta, "conversation_id": conversa.id}


@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
