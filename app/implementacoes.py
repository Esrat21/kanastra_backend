import logging
from .modelos import Divida
from .abstracoes import GeradorBoleto, EnviadorEmail
from .database import ProcessedBoleto
from sqlalchemy.orm import Session
from typing import Set
from .utils import calcular_hash  # Importar de utils.py

logger = logging.getLogger(__name__)

class GeradorBoletoSimulado(GeradorBoleto):
    def gerar(self, db: Session, divida: Divida, boletos_existentes: Set[str]):
        try:
            logger.info(f"Gerando boleto para {divida.nome} no valor de {divida.valor}")
            boleto_hash = calcular_hash(divida)
            if boleto_hash not in boletos_existentes:
                db_boleto = ProcessedBoleto(
                    id=divida.id,
                    nome=divida.nome,
                    documento=divida.documento,
                    email=divida.email,
                    valor=divida.valor,
                    data_vencimento=divida.data_vencimento,
                    hash=boleto_hash
                )
                db.add(db_boleto)
                db.commit()
                boletos_existentes.add(boleto_hash)
        except Exception as e:
            logger.error(f"Erro ao gerar boleto: {e}")
            raise

class EnviadorEmailSimulado(EnviadorEmail):
    def enviar(self, db: Session, email: str, divida: Divida):
        try:
            logger.info(f"Enviando email para {email} sobre a dívida de {divida.valor}")
            # Atualizar o status de envio de email no banco de dados
            boleto = db.query(ProcessedBoleto).filter_by(id=divida.id).first()
            if boleto:
                boleto.email_enviado = True
                db.commit()
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            raise
