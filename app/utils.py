import hashlib
from .modelos import Divida

def calcular_hash(divida: Divida) -> str:
    hash_string = f"{divida.documento}{divida.valor}{divida.data_vencimento}"
    return hashlib.sha256(hash_string.encode()).hexdigest()
