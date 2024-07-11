import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, ProcessedBoleto
from app.modelos import Divida
from app.servicos import calcular_hash, gerar_boleto_sync, enviar_email_sync
from app.implementacoes import GeradorBoletoSimulado, EnviadorEmailSimulado
from app.abstracoes import GeradorBoleto, EnviadorEmail

# Configurar o banco de dados para testes
DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas no banco de dados de teste
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def gerador_boleto():
    return GeradorBoletoSimulado()

@pytest.fixture
def enviador_email():
    return EnviadorEmailSimulado()

def test_calcular_hash():
    divida = Divida(nome="Teste", documento="12345678900", email="teste@example.com", valor=1000.0, data_vencimento="2022-12-31", id="1")
    hash_gerado = calcular_hash(divida)
    assert hash_gerado is not None

def test_gerar_boleto_sync(db_session, gerador_boleto: GeradorBoleto):
    divida = Divida(nome="Teste", documento="12345678900", email="teste@example.com", valor=1000.0, data_vencimento="2022-12-31", id="1")
    boletos_existentes = set()
    gerador_boleto.gerar(db_session, divida, boletos_existentes)
    boleto = db_session.query(ProcessedBoleto).filter_by(id="1").first()
    assert boleto is not None
    assert boleto.nome == "Teste"

def test_enviar_email_sync(db_session, enviador_email: EnviadorEmail):
    divida = Divida(nome="Teste", documento="12345678900", email="teste@example.com", valor=1000.0, data_vencimento="2022-12-31", id="1")
    db_boleto = ProcessedBoleto(
        id=divida.id,
        nome=divida.nome,
        documento=divida.documento,
        email=divida.email,
        valor=divida.valor,
        data_vencimento=divida.data_vencimento,
        hash=calcular_hash(divida)
    )
    db_session.add(db_boleto)
    db_session.commit()
    enviador_email.enviar(db_session, divida.email, divida)
    boleto = db_session.query(ProcessedBoleto).filter_by(id="1").first()
    assert boleto.email_enviado is True
