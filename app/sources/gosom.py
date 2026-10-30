"""Fonte que conversa com o scraper gosom (container 'scraper').

Se o formato da API do gosom mudar um dia, este é o ÚNICO arquivo a ajustar.
"""
import csv
import io

import httpx

from app.config import config
from app.models import Empresa
from app.sources.base import ErroFonte


def _num(v, tipo):
    try:
        return tipo(str(v).replace(",", ".")) if str(v).strip() else None
    except ValueError:
        return None


def _email(v: str) -> str:
    # O gosom pode devolver vários e-mails em formato de lista; pegamos o primeiro.
    v = (v or "").strip().strip("[]").replace('"', "")
    return v.split(",")[0].strip()


def linha_para_empresa(r: dict) -> Empresa:
    return Empresa(
        nome=r.get("title", ""),
        categoria=r.get("category", ""),
        endereco=r.get("address", ""),
        telefone=r.get("phone", ""),
        site=r.get("website", ""),
        email=_email(r.get("emails", "")),
        nota=_num(r.get("review_rating"), float),
        avaliacoes=_num(r.get("review_count"), int),
        latitude=_num(r.get("latitude"), float),
        longitude=_num(r.get("longitude"), float),
        link_maps=r.get("link", ""),
    )


def csv_para_empresas(texto: str) -> list[Empresa]:
    return [linha_para_empresa(r) for r in csv.DictReader(io.StringIO(texto)) if r.get("title")]


class Gosom:
    def __init__(self, base: str | None = None, cliente: httpx.Client | None = None):
        self.base = (base or config.scraper_url).rstrip("/")
        self.http = cliente or httpx.Client(timeout=30)

    def _pedir(self, metodo: str, caminho: str, **kw) -> httpx.Response:
        try:
            r = self.http.request(metodo, f"{self.base}{caminho}", **kw)
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            raise ErroFonte(f"O motor recusou o pedido ({e.response.status_code}): {e.response.text[:300]}") from e
        except httpx.HTTPError as e:
            raise ErroFonte(f"Motor do Google Maps indisponível: {e}") from e

    def criar_busca(self, termo, lat, lon, profundidade) -> str:
        corpo = {
            "name": termo[:60], "keywords": [termo], "lang": "pt", "zoom": 15,
            "lat": str(lat), "lon": str(lon), "radius": 10000, "depth": profundidade,
            "fast_mode": False, "email": True, "max_time": config.tempo_maximo,
        }
        return self._pedir("POST", "/api/v1/jobs", json=corpo).json()["id"]

    def listar(self) -> list[dict]:
        dados = self._pedir("GET", "/api/v1/jobs").json() or []  # vazio vem como null
        return [{"id": j.get("ID") or j.get("id"), "nome": j.get("Name") or j.get("name"),
                 "status": j.get("Status") or j.get("status")} for j in dados]

    def status(self, busca_id: str) -> str:
        j = self._pedir("GET", f"/api/v1/jobs/{busca_id}").json()
        return j.get("Status") or j.get("status") or "working"

    def resultados(self, busca_id: str) -> list[Empresa]:
        return csv_para_empresas(self._pedir("GET", f"/api/v1/jobs/{busca_id}/download").text)
