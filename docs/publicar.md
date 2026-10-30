# Publicar online para a equipe

Resultado: um endereço como `https://leads.seudominio.com.br`, aberto só para os e-mails que você autorizar.

## O que você precisa
1. Um **domínio** (qualquer registrador) com o DNS gerenciado na Cloudflare (conta grátis em cloudflare.com).
2. Uma **máquina que fique ligada** com Docker: seu computador (grátis) ou um VPS Linux com ~4 GB de RAM.

## Passo a passo

### 1. Criar o túnel
Cloudflare -> **Zero Trust** -> **Networks -> Tunnels** -> **Create a tunnel** -> tipo *Cloudflared* -> dê um nome.
Na tela de instalação, copie apenas o **token** (texto longo depois de `--token`).

### 2. Apontar o endereço para o sistema
Na aba **Public Hostname** do túnel: escolha o subdomínio (ex.: `leads`) e seu domínio.
Em *Service*: tipo **HTTP**, URL **`app:8000`**.

### 3. Proteger com login por e-mail (OBRIGATÓRIO)
Zero Trust -> **Access -> Applications -> Add -> Self-hosted**.
- Domínio: o mesmo endereço do passo 2.
- Policy: **Allow** -> *Emails* -> liste os e-mails da equipe.
- Método de login: *One-time PIN* (a pessoa recebe um código por e-mail).

### 4. Subir na máquina
```bash
cd mapa-leads
cp .env.example .env
# edite o .env e preencha:  TUNNEL_TOKEN=cole_o_token_aqui
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d --build
```

### 5. Conferir
- Abra o endereço numa **janela anônima**: deve pedir e-mail e código.
- Teste com um e-mail NÃO autorizado: deve ser recusado.
- Só então compartilhe o link.

## Atualizar depois
```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d --build
```

## Cuidados
- Sem o passo 3, **qualquer pessoa com o link** poderia gastar suas buscas. Não pule.
- A equipe divide o mesmo motor e o mesmo IP: façam **uma busca por vez**.
- IPs de servidor (VPS) costumam ser bloqueados pelo Google com mais facilidade que IPs de casa.
