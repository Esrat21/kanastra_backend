from pydantic import BaseModel

class Divida(BaseModel):
    nome: str
    documento: str
    email: str
    valor: float
    data_vencimento: str  # Correspondente a "debtDueDate" no CSV
    id: str  # Correspondente a "debtId" no CSV
