# Guia completo do Mapa Leads — do zero até o ar

Este guia explica **tudo, na ordem, sem pular nada**. Leia uma parte, faça, confirme que funcionou e só então vá para a próxima. Se algo der errado, vá direto à parte 10 (problemas comuns).

Os comandos são para **Ubuntu** (o seu caso). Tudo que aparece em um bloco de código você copia e cola no **terminal** (Ctrl+Alt+T).

---

## Parte 0 — Entendendo o que você vai montar

### O que o sistema faz
Você digita um nicho (dentistas) e uma cidade (Campinas, SP). O sistema devolve uma tabela com nome, telefone, site, e-mail, nota e endereço das empresas encontradas no Google Maps.

### As peças (use esta imagem mental)
Pense num restaurante:

| Peça | No restaurante | No sistema |
|---|---|---|
| **Tela** (`app/static`) | O salão e o cardápio: o que o cliente vê | A página que você abre no navegador |
| **API** (`app/main.py`) | O garçom: leva o pedido e traz a resposta | Recebe a busca e devolve os resultados |
| **Fonte** (`app/sources/gosom.py`) | O comprador que vai ao mercado | Fala com o motor que lê o Google Maps |
| **Motor** (container `scraper`) | O mercado | O programa de terceiros (gosom) que abre um navegador invisível e lê o Google Maps |
| **Geocodificador** (`app/geo.py`) | O mapa na parede | Transforma "Campinas, SP" em latitude/longitude |

### O que é Docker, de uma vez por todas
O Docker é uma **caixa fechada** que já vem com o programa e tudo que ele precisa para funcionar. Você não instala Python, Chromium nem bibliotecas no seu Ubuntu: cada caixa (**container**) traz os dela. Por isso o mesmo sistema roda igual no seu computador e num servidor.

- **Imagem** = a receita/molde da caixa (baixada da internet).
- **Container** = a caixa em funcionamento, criada a partir da imagem.
- **Docker Compose** = um arquivo (`docker-compose.yml`) que descreve *várias caixas juntas* e como elas se conectam. Um único comando liga todas.

Neste projeto são **2 containers**: `scraper` (o motor) e `app` (o nosso sistema). O código do `app` fica na pasta do projeto no seu disco e é copiado para dentro da caixa quando você roda `--build`.

---

## Parte 1 — Preparar o computador

### 1.1 Conferir se o Docker está instalado e ligado
```bash
docker --version
docker compose version
docker ps
```
- Os dois primeiros mostram versões. Se aparecer "command not found", o Docker não está instalado.
- `docker ps` lista os containers ligados. Uma lista vazia (só o cabeçalho) é **normal e boa**.
- Se aparecer `Cannot connect to the Docker daemon`, o Docker está instalado mas **desligado**. Ligue o Docker Desktop pelo menu de aplicativos, ou:
```bash
systemctl --user start docker-desktop
```
Espere cerca de 1 minuto e rode `docker ps` de novo.

### 1.2 Conferir espaço e memória
O motor usa um navegador por trás, então precisa de folga:
```bash
free -h      # procure "Mem:", ideal ter 4 GB ou mais
df -h ~      # procure espaço livre, ideal 10 GB ou mais
```

---

## Parte 2 — Obter o projeto

Você recebeu o arquivo `mapa-leads-etapa1.zip`. Descompacte:
```bash
mkdir -p ~/mapa-leads
unzip ~/Downloads/mapa-leads-etapa1.zip -d ~/mapa-leads
cd ~/mapa-leads
ls
```
Explicando: `mkdir -p` cria a pasta, `unzip ... -d` extrai o conteúdo nela, `cd` entra na pasta e `ls` lista o que há dentro. Você deve ver `app`, `docs`, `tests`, `Dockerfile`, `docker-compose.yml`, `README.md`...

> Se o `unzip` não existir: `sudo apt install unzip`.

---

## Parte 3 — Conhecendo cada arquivo

```
mapa-leads/
├── docker-compose.yml            Liga os 2 containers (scraper + app)
├── docker-compose.cloudflare.yml EXTRA: liga o túnel para ir à internet
├── Dockerfile                    Receita para montar a caixa do "app"
├── requirements.txt              Lista das bibliotecas Python usadas
├── .env.example                  Modelo de configurações
├── app/
│   ├── main.py                   As rotas da API (o "garçom")
│   ├── models.py                 O formato de uma Empresa e de uma busca
│   ├── config.py                 Limites e endereços configuráveis
│   ├── geo.py                    Cidade -> coordenadas
│   ├── sources/base.py           O "contrato" de qualquer fonte de dados
│   ├── sources/gosom.py          Fala com o motor (único arquivo que o conhece)
│   └── static/                   A tela: index.html, app.js, style.css
├── tests/test_etapa1.py          Testes automáticos
└── docs/                         Estes guias
```

### Lendo os arquivos importantes

**`docker-compose.yml`**
- `scraper`: usa a imagem pronta `gosom/google-maps-scraper:v1.18.1` (versão **fixa** de propósito: não muda sozinha e quebra). `command` liga o modo web. `shm_size: 1gb` dá memória compartilhada ao Chromium, que trava sem isso. `volumes` guarda os dados fora da caixa para não se perderem ao reiniciar.
- `app`: `build: .` significa "monte a caixa a partir do Dockerfile desta pasta". `SCRAPER_URL` diz onde está o motor (dentro da rede do Docker, o nome `scraper` funciona como endereço). `ports: "127.0.0.1:8000:8000"` publica o sistema **só no seu computador** (o `127.0.0.1` impede que outros acessem pela rede).
- O `scraper` **não** publica porta nenhuma: só o `app` consegue falar com ele. Isso é segurança.

**`app/sources/base.py` e `gosom.py`** — o coração da manutenção. `base.py` diz: "toda fonte precisa saber criar busca, listar, informar status e entregar resultados". `gosom.py` cumpre isso falando com o motor. Se o motor mudar ou você quiser trocar por outra fonte, você mexe **só** aqui.

**`app/config.py`** — limites de segurança: profundidade padrão 5, máxima 20, tempo máximo de 300 s por busca.

**`app/main.py`** — 4 rotas: `/api/saude` (está vivo?), `POST /api/buscas` (criar), `GET /api/buscas` (listar), `GET /api/buscas/{id}` (ver andamento/resultados).

---

## Parte 4 — Subir o sistema

```bash
cd ~/mapa-leads
docker compose up -d --build
```
Palavra por palavra:
- `docker compose` — usa o arquivo `docker-compose.yml` da pasta.
- `up` — cria e liga os containers.
- `-d` — "detached": roda em segundo plano e devolve o terminal para você.
- `--build` — monta (ou remonta) a caixa do `app` com o código atual.

**O que esperar:** na **primeira vez** demora vários minutos, porque baixa as imagens (a do motor é grande). Depois fica rápido.

### Conferir
```bash
docker compose ps
```
Os serviços `scraper` e `app` devem estar com estado **running**. Depois:
```bash
curl http://localhost:8000/api/saude
```
Deve responder `{"ok":true}`. Se sim, o seu sistema está de pé.

### Ver o que está acontecendo (logs)
```bash
docker compose logs -f app       # Ctrl+C para sair
docker compose logs -f scraper
```

---

## Parte 5 — Primeira busca

1. Abra **http://localhost:8000** no navegador.
2. Em "O que buscar": `dentistas`. Em "Cidade": `Campinas, SP`. Em "Quantidade": **Pequena (teste rápido)**.
3. Clique em **Buscar empresas**.
4. A mensagem mostra "Buscando no Google Maps… (Ns)". **Pode levar alguns minutos**; não feche a página.
5. Ao terminar aparece a tabela. Use "Filtrar na lista…" para filtrar por qualquer texto.

**Por que "Pequena" primeiro?** Menos pedidos ao Google, menos risco de bloqueio, e você valida que tudo funciona.

### Regras de boa convivência com o Google
- Faça **uma busca por vez**.
- Não repita a mesma busca várias vezes seguidas.
- Se começarem a vir resultados vazios ou falhas, espere de 30 minutos a algumas horas.

---

## Parte 6 — O que acontece por trás de uma busca

1. **Tela** → envia `POST /api/buscas` com `{termo, cidade, profundidade}`.
2. **`main.py`** → valida (termo e cidade com ao menos 2 letras) e limita a profundidade a 20.
3. **`geo.py`** → pergunta ao OpenStreetMap a latitude/longitude da cidade.
4. **`gosom.py`** → manda o motor criar o trabalho ("dentistas em Campinas, SP", com as coordenadas) e recebe um `id`.
5. **Motor** → abre o Chromium invisível, rola a lista do Google Maps e visita cada empresa.
6. **Tela** → a cada 3 segundos pergunta `GET /api/buscas/{id}`: `working` (trabalhando), `ok` (pronto) ou `failed` (falhou).
7. Com `ok`, **`gosom.py`** baixa o CSV do motor e converte cada linha numa `Empresa`; a tela desenha a tabela.

---

## Parte 7 — Rodar os testes (opcional, mas recomendado)

Testes são "verificações automáticas": se algo quebrar numa mudança futura, eles avisam na hora.
```bash
cd ~/mapa-leads
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
Explicando: `venv` cria um ambiente Python isolado só para o projeto; `. .venv/bin/activate` entra nele; `pip install` instala as bibliotecas; `pytest` roda os testes. Esperado: **7 passed**. Para sair do ambiente: `deactivate`.

---

## Parte 8 — Guardar o projeto no GitHub

Por que: ter o histórico de cada mudança, poder voltar atrás e baixar o sistema em qualquer servidor com um comando.

### 8.1 Criar o repositório
Em github.com: **New repository** → nome `mapa-leads` → marque **Private** (privado, recomendado) → **não** marque README/.gitignore (o projeto já tem) → *Create repository*.

### 8.2 Enviar os arquivos
Dentro da pasta do projeto:
```bash
git init -b main
git add -A
git commit -m "Etapa 1: buscar e listar empresas"
git remote add origin https://github.com/SEU_USUARIO/mapa-leads.git
git push -u origin main
```
- `git init -b main` — transforma a pasta num repositório (ramo principal `main`).
- `git add -A` — separa todos os arquivos para o próximo registro.
- `git commit -m` — registra uma "foto" do projeto com uma descrição.
- `git remote add origin` — diz qual é o endereço do repositório no GitHub.
- `git push -u origin main` — envia para lá.

Se `git commit` reclamar de identidade, rode antes (uma vez):
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```
**Senha:** o GitHub não aceita a senha da conta no terminal. Use o GitHub CLI (`sudo apt install gh` e depois `gh auth login`) ou crie um *Personal Access Token* e use-o no lugar da senha.

### 8.3 O ciclo de atualização (combinado com você)
1. Eu termino uma etapa e **aviso você** com um novo ZIP.
2. Você descompacta por cima da pasta do projeto (ou substitui os arquivos), e roda:
```bash
git add -A && git commit -m "Etapa 2" && git push
```
3. No servidor, para aplicar:
```bash
git pull
docker compose up -d --build
```
(Se usar o túnel, acrescente os dois `-f` como na parte 9.)

---

## Parte 9 — Colocar online para outras pessoas

Resultado: `https://leads.seudominio.com.br`, acessível **só pelos e-mails que você autorizar**.

### 9.1 O que você precisa
- Um **domínio** (ex.: `seudominio.com.br`) com o DNS gerenciado pela **Cloudflare** (conta grátis em cloudflare.com; adicione o domínio e troque os servidores de nome conforme eles instruírem).
- Uma **máquina sempre ligada** com Docker: seu computador (grátis, mas só funciona enquanto estiver ligado) ou um **VPS** Linux com ~4 GB de RAM (funciona 24 h).
- No VPS, instale o Docker Engine: https://docs.docker.com/engine/install/ubuntu/ e baixe o projeto com `git clone`.

### 9.2 Como funciona o túnel (para você entender o que está fazendo)
Normalmente, para um site ficar online é preciso abrir uma porta no servidor, o que expõe a máquina. O **Cloudflare Tunnel** inverte: um container (`cloudflared`) **liga para fora** na Cloudflare, e a Cloudflare entrega as visitas por esse canal. Nenhuma porta é aberta, e o tráfego chega com HTTPS (cadeado) automaticamente.

### 9.3 Passo a passo
**Passo 1 — Criar o túnel.** Cloudflare → **Zero Trust** → **Networks → Tunnels** → **Create a tunnel** → *Cloudflared* → dê um nome. Na tela seguinte, copie só o **token** (o texto longo depois de `--token`).

**Passo 2 — Endereço.** Na aba **Public Hostname**: Subdomain `leads`, Domain `seudominio.com.br`, Service **HTTP** com URL `app:8000`.

**Passo 3 — Proteção (obrigatório).** Zero Trust → **Access → Applications → Add an application → Self-hosted**. Informe o mesmo endereço do passo 2. Crie uma **Policy**: ação *Allow*, regra *Emails* com os e-mails da equipe. Quem tentar entrar recebe um código por e-mail e só passa se o e-mail estiver na lista.

**Passo 4 — Subir.**
```bash
cp .env.example .env
nano .env          # apague o # da linha TUNNEL_TOKEN= e cole o token; salve com Ctrl+O, Enter, Ctrl+X
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d --build
```
O segundo `-f` soma o arquivo do túnel ao principal.

**Passo 5 — Conferir.**
1. Abra o endereço numa **janela anônima**: deve pedir e-mail.
2. Entre com um e-mail autorizado: o sistema abre.
3. Tente com um e-mail não autorizado: deve ser recusado.
4. Só depois compartilhe o link.

### 9.4 Por que o login da Cloudflare é obrigatório agora
O sistema ainda não tem login próprio (vem na Etapa 4). Sem o Access, qualquer pessoa com o link poderia gastar as suas buscas e expor os dados.

### 9.5 Limitações reais
- A equipe usa o **mesmo motor e o mesmo IP**: uma busca por vez.
- O Google costuma bloquear **IPs de servidor** mais que IPs residenciais. Se as buscas falharem muito no VPS, a solução é usar proxy.
- O histórico ainda não é salvo (vem na Etapa 2): ao terminar, exporte ou copie o que precisar.

---

## Parte 10 — Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker desligado | `systemctl --user start docker-desktop` e aguarde |
| `permission denied` ao rodar docker | Usuário fora do grupo docker (Docker Engine) | `sudo usermod -aG docker $USER` e saia/entre na sessão |
| `port is already allocated` (8000) | Outra coisa usa a porta | Pare-a, ou troque `8000:8000` por `8001:8000` no compose |
| Tela abre, mas a busca dá "Motor do Google Maps indisponível" | `scraper` ainda iniciando ou parado | `docker compose ps`, depois `docker compose logs scraper` |
| "Não encontrei a cidade" | Nome ambíguo | Use `Cidade, UF` (ex.: `Natal, RN`) |
| Busca termina sem resultados | Termo estreito ou IP limitado | Termo mais comum; espere e tente de novo |
| Busca "failed" repetida | Bloqueio temporário do Google | Pare por algumas horas; use proxy se for recorrente |
| Domínio mostra erro 502/1033 | Túnel desligado ou token errado | `docker compose -f ... logs cloudflared` e confira o `.env` |
| Mudei código e nada mudou | Esqueceu de remontar | `docker compose up -d --build` |

Comandos úteis: `docker compose ps` (estado), `docker compose restart app` (reiniciar), `docker compose down` (desligar tudo), `docker compose down -v` (desligar **e apagar** os dados do motor).

---

## Parte 11 — Segurança e uso responsável

- Ler o Google Maps assim vai contra os termos do Google e pode causar bloqueio temporário de IP. Sua conta Google não é afetada.
- Telefones e e-mails são **dados pessoais** (LGPD): use para contato comercial legítimo, ofereça opção de não receber mais mensagens e não revenda a lista.
- Nunca publique o sistema sem a proteção do Access.
- Mantenha o repositório **privado** e nunca coloque o `TUNNEL_TOKEN` no GitHub (o `.gitignore` já ignora o `.env`).

---

## Parte 12 — O que vem a seguir

| Etapa | O que entrega |
|---|---|
| 1 (esta) | Buscar e listar |
| 2 | Salvar histórico (banco SQLite) e exportar para Excel/CSV |
| 3 | Instagram da empresa (lido do site da própria empresa) |
| 4 | Login próprio, usuários e ajustes para produção |

Caminho de crescimento já previsto: trocar SQLite por PostgreSQL, trocar a fonte (API oficial do Google), adicionar filtros por CNAE ou nicho, enviar para CRM.

---

## Glossário rápido

- **Container**: caixa isolada com um programa rodando.
- **Imagem**: molde usado para criar containers.
- **Compose**: arquivo que liga vários containers juntos.
- **API**: conjunto de endereços que um programa oferece para outros programas.
- **CSV**: arquivo de tabela em texto simples (abre no Excel).
- **Token**: senha longa gerada para um programa (não é a sua senha pessoal).
- **Túnel**: canal seguro que leva visitas da internet até o seu sistema sem abrir portas.
- **VPS**: computador alugado, ligado 24 h, em um datacenter.
- **Commit / push / pull**: registrar mudanças / enviar para o GitHub / baixar do GitHub.
