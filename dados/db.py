import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuração da URL do Banco de Dados
# A senha correta é SophieBancodeDados (sem o colchete final, como o usuário confirmou)
db_user = "postgres"
db_pass = urllib.parse.quote_plus("SophieBancodeDados")
db_host = "db.sohgxqepuufdljuwtlqy.supabase.co"
db_port = "5432"
db_name = "postgres"

DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Criando a Engine do SQLAlchemy
# pool_pre_ping ajuda a lidar com conexões derrubadas pelo banco na nuvem
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Criando a classe Base para nossos modelos e o gerador de sessões
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependência do FastAPI para pegar uma sessão do banco e fechar após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def iniciar_banco():
    """
    Cria todas as tabelas no banco de dados se elas não existirem.
    """
    Base.metadata.create_all(bind=engine)
