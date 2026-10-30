"""Transforma 'Campinas, SP' em latitude/longitude usando o OpenStreetMap (grátis)."""
import httpx


class CidadeNaoEncontrada(Exception):
    pass


def geocodificar(cidade: str, cliente: httpx.Client | None = None) -> tuple[float, float]:
    http = cliente or httpx.Client(timeout=15)
    try:
        r = http.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": cidade, "format": "json", "limit": 1},
            headers={"User-Agent": "mapa-leads/1.0 (uso pessoal)"},
        )
        r.raise_for_status()
        achados = r.json()
    except httpx.HTTPError as e:
        raise CidadeNaoEncontrada(f"Não consegui consultar o mapa: {e}") from e
    if not achados:
        raise CidadeNaoEncontrada(f"Não encontrei a cidade '{cidade}'. Tente 'Cidade, UF'.")
    return float(achados[0]["lat"]), float(achados[0]["lon"])
