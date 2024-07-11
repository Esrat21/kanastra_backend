from sqlalchemy import create_engine, Column, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

# Caminho do banco de dados
DATABASE_FILE = "/home/jovyan/app/test.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Criar o engine do SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProcessedBoleto(Base):
    __tablename__ = "processed_boletos"
    id = Column(String, primary_key=True, index=True)
    nome = Column(String, index=True)
    documento = Column(String, index=True)
    email = Column(String, index=True)
    valor = Column(Float)
    data_vencimento = Column(String)
    hash = Column(String, unique=True, index=True)
    email_enviado = Column(Boolean, default=False)

# Criar as tabelas no banco de dados se o arquivo não existir
if not os.path.exists(DATABASE_FILE):
    Base.metadata.create_all(bind=engine)

# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
