import os
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuração da URL do Banco de Dados via variáveis de ambiente (Vercel/Supabase)
def get_postgres_url():
    """Constrói URL do PostgreSQL a partir de variáveis de ambiente."""
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = urllib.parse.quote_plus(os.getenv("DB_PASS", "SophieBancodeDados"))
    db_host = os.getenv("DB_HOST", "db.sohgxqepuufdljuwtlqy.supabase.co")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Usa POSTGRES_URL do ambiente (Vercel) ou constrói a partir das partes
POSTGRES_URL = os.getenv("POSTGRES_URL") or get_postgres_url()
SQLITE_URL = "sqlite:///./sophie_local.db"

_engine = None

def get_engine():
    """Retorna engine singleton (lazy)."""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Conectado ao PostgreSQL (Supabase)!")
        except Exception as e:
            print(f"PostgreSQL indisponível ({e}). Usando SQLite local...")
            _engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
            print("Conectado ao SQLite local!")
    return _engine

# Criando a classe Base para nossos modelos e o gerador de sessões
Base = declarative_base()

def get_session_local():
    """Retorna SessionLocal ligado ao engine atual."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependência do FastAPI para pegar uma sessão do banco e fechar após o uso.
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def iniciar_banco():
    """
    Cria todas as tabelas no banco de dados.
    DROP + CREATE para garantir schema limpo (remove user_id antigo).
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)