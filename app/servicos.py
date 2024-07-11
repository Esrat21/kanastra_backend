import csv
from typing import List, Set, Tuple
from .modelos import Divida
from .database import SessionLocal, ProcessedBoleto
from .implementacoes import GeradorBoletoSimulado, EnviadorEmailSimulado
import logging
from sqlalchemy.orm import Session
from .utils import calcular_hash  # Importar de utils.py

logger = logging.getLogger(__name__)

gerador_boleto = GeradorBoletoSimulado()
enviador_email = EnviadorEmailSimulado()

# Recupera boletos já processados do banco de dados.
def get_processed_boletos(db: Session):
    return {boleto.hash for boleto in db.query(ProcessedBoleto).all()}

# Processa o arquivo CSV e retorna uma lista de dívidas e um conjunto de novos boletos.
async def processar_csv(file, boletos_existentes: Set[str]) -> Tuple[List[Divida], Set[str]]:
    dividas = []
    novos_boletos = set()
    
    try:
        content = file.file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(content)
        
        for row in reader:
            divida = Divida(
                nome=row['name'],
                documento=row['governmentId'],
                email=row['email'],
                valor=float(row['debtAmount']),
                data_vencimento=row['debtDueDate'],
                id=row['debtId']
            )
            
            divida_hash = calcular_hash(divida)
            if divida_hash not in boletos_existentes:
                dividas.append(divida)
                novos_boletos.add(divida_hash)
    
    except Exception as e:
        logger.error(f"Erro ao processar o CSV: {e}")
        raise
    
    return dividas, novos_boletos

def gerar_boleto_sync(db: Session, divida: Divida, boletos_existentes: Set[str]):
    gerador_boleto.gerar(db, divida, boletos_existentes)

def enviar_email_sync(db: Session, email: str, divida: Divida):
    enviador_email.enviar(db, email, divida)
