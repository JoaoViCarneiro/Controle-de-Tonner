"""
models.py
Representação das entidades do sistema.
VERSÃO COM CONTADOR ÚNICO POR MÁQUINA
"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Maquina:
    """Representa uma impressora"""
    id: Optional[int] = None
    nome: str = ""
    modelo: str = ""
    tipo: str = "P&B"
    contador_atual: int = 0  # SEMPRE o MAIOR valor registrado
    data_cadastro: str = ""

    @property
    def cores_tonner(self) -> List[str]:
        if self.tipo == "P&B":
            return ["Preto"]
        else:
            return ["Preto", "Ciano", "Magenta", "Amarelo"]

    def __str__(self):
        return f"{self.nome} (ID: {self.id})"

@dataclass
class tonner:
    """Representa um tonner físico (cada unidade)"""
    id: Optional[int] = None
    maquina_id: int = 0
    cor: str = ""
    data_instalacao: str = ""
    data_retirada: str = ""
    contador_inicial: int = 0
    contador_final: int = 0
    custo: float = 0.0
    observacao: str = ""
    data_registro: str = ""

    @property
    def total_impressoes(self) -> int:
        """Calcula o total de impressões feitas com este tonner"""
        return self.contador_final - self.contador_inicial if self.contador_final > 0 else 0

    @property
    def rendimento_abaixo(self) -> bool:
        """Verifica se o rendimento está abaixo do esperado (14500)"""
        return self.total_impressoes < 14500 if self.total_impressoes > 0 else False

    @property
    def custo_por_pagina(self) -> float:
        """Calcula o custo por página deste tonner"""
        if self.total_impressoes > 0:
            return self.custo / self.total_impressoes
        return 0.0

    def __str__(self):
        status = "Ativo" if not self.data_retirada else f"Finalizado: {self.total_impressoes} págs"
        return f"{self.cor} - {status}"

@dataclass
class Rendimento:
    """Resultado do cálculo de rendimento por tonner"""
    cor: str
    data_instalacao: str
    data_retirada: str
    contador_inicial: int
    contador_final: int
    total_impressoes: int
    custo: float
    custo_pagina: float
    rendimento_abaixo: bool
    maquina_nome: str
    maquina_id: int

    @property
    def periodo(self) -> str:
        return f"{self.data_instalacao} até {self.data_retirada}"