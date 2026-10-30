"""Contrato da 'fonte' de empresas.

Qualquer fonte (scraper hoje, API oficial do Google amanhã) só precisa
implementar estes 3 métodos. O resto do sistema não sabe de onde os dados vêm.
"""
from typing import Protocol

from app.models import Empresa


class ErroFonte(Exception):
    """A fonte não respondeu ou recusou o pedido."""


class Fonte(Protocol):
    def criar_busca(self, termo: str, lat: float, lon: float, profundidade: int) -> str: ...
    def listar(self) -> list[dict]: ...
    def status(self, busca_id: str) -> str: ...  # "working" | "ok" | "failed"
    def resultados(self, busca_id: str) -> list[Empresa]: ...
