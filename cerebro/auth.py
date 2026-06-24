from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Configuração para hash de senhas (BCrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Chave secreta para assinar os tokens (Numa app real, use variáveis de ambiente)
SECRET_KEY = "SOPHIE_SUPER_SECRET_KEY_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias logado

def hash_senha(senha: str) -> str:
    """Criptografa uma senha."""
    return pwd_context.hash(senha)

def verificar_senha(senha_limpa: str, senha_hash: str) -> bool:
    """Verifica se a senha bate com o hash salvo."""
    return pwd_context.verify(senha_limpa, senha_hash)

def criar_token_acesso(dados: dict, expira_delta: Optional[timedelta] = None) -> str:
    """Gera um JWT com validade para o usuário logado."""
    a_codificar = dados.copy()
    if expira_delta:
        expirar_em = datetime.utcnow() + expira_delta
    else:
        expirar_em = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    a_codificar.update({"exp": expirar_em})
    token_jwt = jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def verificar_token(token: str) -> dict:
    """Tenta ler os dados dentro de um JWT. Levanta erro se estiver vencido ou inválido."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
