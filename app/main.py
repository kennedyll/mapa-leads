"""A API do sistema. Cada rota faz uma coisa simples e delega o trabalho pesado."""
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app import geo
from app.config import config
from app.models import Empresa, NovaBusca
from app.sources.base import ErroFonte, Fonte
from app.sources.gosom import Gosom

app = FastAPI(title="Mapa Leads")


def pegar_fonte() -> Fonte:
    return Gosom()


@app.get("/api/saude")
def saude():
    return {"ok": True}


@app.post("/api/buscas", status_code=201)
def criar_busca(dados: NovaBusca, fonte: Fonte = Depends(pegar_fonte)):
    prof = min(dados.profundidade or config.profundidade_padrao, config.profundidade_maxima)
    try:
        lat, lon = geo.geocodificar(dados.cidade)
        busca_id = fonte.criar_busca(f"{dados.termo} em {dados.cidade}", lat, lon, prof)
    except geo.CidadeNaoEncontrada as e:
        raise HTTPException(422, str(e))
    except ErroFonte as e:
        raise HTTPException(503, str(e))
    return {"id": busca_id}


@app.get("/api/buscas")
def listar_buscas(fonte: Fonte = Depends(pegar_fonte)):
    try:
        return fonte.listar()
    except ErroFonte as e:
        raise HTTPException(503, str(e))


@app.get("/api/buscas/{busca_id}")
def ver_busca(busca_id: str, fonte: Fonte = Depends(pegar_fonte)):
    try:
        status = fonte.status(busca_id)
        empresas: list[Empresa] = fonte.resultados(busca_id) if status == "ok" else []
    except ErroFonte as e:
        raise HTTPException(503, str(e))
    return {"id": busca_id, "status": status, "empresas": empresas}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
