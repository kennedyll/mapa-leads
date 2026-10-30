# Mapa Leads

Sistema simples para montar listas de empresas do Google Maps por nicho e cidade.
Feito em **Python (FastAPI)** + uma tela em HTML/JS puro. Sem build, sem framework pesado.

## Como rodar (precisa só de Docker)

```bash
git clone <URL-DO-SEU-REPOSITORIO> mapa-leads
cd mapa-leads
docker compose up -d --build
```

Abra **http://localhost:8000**, digite um nicho (ex.: `dentistas`), uma cidade (ex.: `Campinas, SP`) e clique em *Buscar empresas*.

Para parar: `docker compose down`. Para ver logs: `docker compose logs -f app`.

## Mapa do projeto

| Arquivo | Para que serve |
|---|---|
| `app/main.py` | As rotas da API (criar busca, ver andamento/resultados) |
| `app/sources/gosom.py` | Conversa com o motor que lê o Google Maps. **Único** arquivo que sabe disso |
| `app/sources/base.py` | O "contrato" que qualquer fonte de dados precisa seguir |
| `app/geo.py` | Cidade -> latitude/longitude (OpenStreetMap, grátis) |
| `app/models.py` | O formato de uma `Empresa` e de uma busca |
| `app/config.py` | Configurações (limites, endereço do motor) |
| `app/static/` | A tela (`index.html`, `app.js`, `style.css`) |
| `tests/` | Testes automáticos |

Guia completo, do zero até o ar: [docs/guia-completo.md](docs/guia-completo.md). Detalhe técnico da Etapa 1: [docs/etapa-1.md](docs/etapa-1.md).

## Publicar online

Veja [docs/publicar.md](docs/publicar.md) (Cloudflare Tunnel + login por e-mail).

## Etapas

1. Buscar e listar empresas  <- **você está aqui**
2. Salvar histórico e exportar (Excel/CSV)
3. Instagram da empresa
4. Login e publicação online

## Avisos

- Ler o Google Maps assim é contra os termos do Google e pode causar bloqueio temporário do seu IP. Use com moderação (uma busca por vez).
- Telefones e e-mails são dados pessoais: respeite a LGPD ao contatar.

Motor de coleta: [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (MIT, Georgios Komninos).
