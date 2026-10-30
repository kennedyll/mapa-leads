"""Os 'formatos' dos dados. Todo o sistema fala a mesma língua: Empresa."""
from pydantic import BaseModel, Field


class Empresa(BaseModel):
    nome: str = ""
    categoria: str = ""
    endereco: str = ""
    telefone: str = ""
    site: str = ""
    email: str = ""
    nota: float | None = None
    avaliacoes: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    link_maps: str = ""


class NovaBusca(BaseModel):
    termo: str = Field(min_length=2, max_length=120, description="Ex.: dentistas")
    cidade: str = Field(min_length=2, max_length=120, description="Ex.: Campinas, SP")
    profundidade: int | None = Field(default=None, ge=1)
