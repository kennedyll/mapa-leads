"""Configurações do sistema. Lê variáveis de ambiente (ou do arquivo .env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Onde está o motor (gosom) que lê o Google Maps.
    scraper_url: str = "http://localhost:8080"
    # Limites de segurança para não pedir demais e ser bloqueado pelo Google.
    profundidade_padrao: int = 5
    profundidade_maxima: int = 20
    # Tempo máximo (segundos) que uma busca pode demorar.
    tempo_maximo: int = 600


config = Config()
