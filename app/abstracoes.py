from abc import ABC, abstractmethod
from .modelos import Divida

class GeradorBoleto(ABC):
    @abstractmethod
    def gerar(self, divida: Divida):
        pass

class EnviadorEmail(ABC):
    @abstractmethod
    def enviar(self, email: str, divida: Divida):
        pass
