from fastapi.testclient import TestClient

from app import geo
from app.main import app, pegar_fonte
from app.models import Empresa
from app.sources.base import ErroFonte
from app.sources.gosom import csv_para_empresas

CSV = ('title,category,address,website,phone,review_count,review_rating,latitude,longitude,link,emails\n'
       'Clínica A,Dentista,Rua 1,https://a.com,1199,10,"4,5",-22.9,-47.0,https://maps.google.com/x,"[""a@a.com"",""b@a.com""]"\n'
       ',sem nome,,,,,,,,,\n')


class FonteFalsa:
    def __init__(self, status="ok"): self._s = status
    def criar_busca(self, termo, lat, lon, prof): self.ultimo = (termo, lat, lon, prof); return "abc"
    def listar(self): return [{"id": "abc", "nome": "x", "status": self._s}]
    def status(self, i): return self._s
    def resultados(self, i): return [Empresa(nome="Clínica A")]


def cliente(fonte, monkeypatch=None):
    app.dependency_overrides[pegar_fonte] = lambda: fonte
    return TestClient(app)


def test_csv_vira_empresas():
    e = csv_para_empresas(CSV)
    assert len(e) == 1 and e[0].nome == "Clínica A"
    assert e[0].nota == 4.5 and e[0].avaliacoes == 10 and e[0].email == "a@a.com"


def test_criar_busca_limita_profundidade(monkeypatch):
    monkeypatch.setattr(geo, "geocodificar", lambda c: (1.0, 2.0))
    f = FonteFalsa()
    r = cliente(f).post("/api/buscas", json={"termo": "dentistas", "cidade": "Campinas", "profundidade": 999})
    assert r.status_code == 201 and r.json() == {"id": "abc"}
    assert f.ultimo == ("dentistas em Campinas", 1.0, 2.0, 20)


def test_cidade_inexistente(monkeypatch):
    def erro(c): raise geo.CidadeNaoEncontrada("não achei")
    monkeypatch.setattr(geo, "geocodificar", erro)
    assert cliente(FonteFalsa()).post("/api/buscas", json={"termo": "ab", "cidade": "zz"}).status_code == 422


def test_validacao_termo_curto():
    assert cliente(FonteFalsa()).post("/api/buscas", json={"termo": "a", "cidade": "zz"}).status_code == 422


def test_ver_busca_pronta_e_andamento():
    assert cliente(FonteFalsa("ok")).get("/api/buscas/abc").json()["empresas"][0]["nome"] == "Clínica A"
    assert cliente(FonteFalsa("working")).get("/api/buscas/abc").json()["empresas"] == []


def test_motor_fora_do_ar():
    class Fora(FonteFalsa):
        def listar(self): raise ErroFonte("fora")
    assert cliente(Fora()).get("/api/buscas").status_code == 503


def test_tela_servida():
    assert "Mapa Leads" in TestClient(app).get("/").text
