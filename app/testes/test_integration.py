import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base, ProcessedBoleto
from contextlib import contextmanager

# Configurar o banco de dados para testes
DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas no banco de dados de teste
Base.metadata.create_all(bind=engine)

# Context manager para criar e finalizar a sessão do banco de dados
@contextmanager
def override_get_db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# Substituir a dependência do banco de dados pelo banco de dados de teste
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_upload_file(client: TestClient):
    response = await client.post("/uploadfile/", files={"file": ("test.csv", "name,governmentId,email,debtAmount,debtDueDate,debtId\nJohn Doe,11111111111,johndoe@example.com,1000.0,2022-12-31,1")})
    print(response.json())  # Adicionar print para depuração
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Arquivo processado com sucesso, emails serão enviados em background"}

    with override_get_db() as db_session:
        boleto = db_session.query(ProcessedBoleto).filter_by(id="1").first()
        assert boleto is not None
        assert boleto.nome == "John Doe"
        assert boleto.email_enviado is True
