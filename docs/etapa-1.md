# Etapa 1 — Buscar e listar empresas (guia didático)

## A ideia em uma frase
Você escreve "dentistas" + "Campinas, SP"; o sistema transforma a cidade em coordenadas, pede ao motor para ler o Google Maps e mostra as empresas numa tabela.

## O caminho de uma busca
1. **Tela** (`app/static/app.js`) envia `POST /api/buscas` com termo, cidade e quantidade.
2. **`main.py`** valida os dados e chama `geo.py` para achar latitude/longitude.
3. **`main.py`** pede à *fonte* (`sources/gosom.py`) que crie a busca; recebe um `id`.
4. A tela pergunta `GET /api/buscas/{id}` a cada 3 segundos. O status vai de `working` para `ok`.
5. Com `ok`, a fonte baixa o CSV do motor e converte cada linha em uma `Empresa`. A tela desenha a tabela.

## Por que é fácil de manter
- **Uma peça por arquivo.** Se o Google mudar algo e o motor quebrar, você só mexe em `sources/gosom.py`.
- **Fonte trocável.** `sources/base.py` define o contrato. Para usar a API oficial do Google no futuro, cria-se `sources/google_places.py` com os mesmos 4 métodos; o resto do sistema não muda.
- **Tudo tem teste.** `pytest` roda em 1 segundo e avisa se algo quebrou.
- **Limites de segurança** em `config.py` (profundidade máxima 20) evitam pedir demais e ser bloqueado.

## Como rodar os testes (opcional)
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## O que ainda NÃO existe (vem nas próximas etapas)
Histórico salvo, exportar para Excel, Instagram, login. Por enquanto os resultados vivem no motor enquanto o container existir.
