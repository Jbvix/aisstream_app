# Passo 2 — Configurar o Pull / Deploy do GitHub para o cPanel

Guia operacional para puxar o código do GitHub (`Jbvix/aisstream_app`) para a
aplicação hospedada no cPanel (`https://tuglife.live/aisstream/`).

> **Status atual (diagnóstico):** o deploy automático **ainda não está
> confiável**. Há dois bloqueios reais identificados no repositório:
> 1. **Não existe `.cpanel.yml`** na raiz (o `DEPLOY_CPANEL.md` afirma que
>    existe, mas o arquivo **não está versionado**).
> 2. **Arquivos de runtime estão versionados** (`saa_maneuvers.json`,
>    `tug_geofence_stats.json`, `saa_schedule_monitor.json`,
>    `strategy_memory.json`). A aplicação reescreve esses arquivos em produção,
>    deixando a *working tree* "suja" — o que produz exatamente o erro do
>    `CPANEL_GIT_ERROR.log`:
>    `error: Entry 'data/users/default/saa_maneuvers.json' not uptodate. Cannot merge.`
>
> Os dois itens são resolvidos na **Seção 4** abaixo (correção recomendada).

---

## 1. Como o cPanel "Git Version Control" funciona

O cPanel mantém um **clone do repositório** dentro da conta. Fluxo:

```
GitHub (origin)  ──(Update from Remote / Pull)──►  Clone no cPanel  ──(Deploy HEAD Commit)──►  DEPLOYPATH (app em produção)
```

- **Pull / Update from Remote**: traz os commits novos do GitHub para o clone.
- **Deploy HEAD Commit**: executa as tarefas do `.cpanel.yml` (copiar arquivos
  para o `DEPLOYPATH`, reiniciar app, etc.).
- O Deploy **só roda se a working tree do clone estiver limpa** e existir um
  `.cpanel.yml` válido.

Dados do ambiente (das telas do cPanel):
- **Repository Path:** `/home/c62gtwye66po/aisstream_app`
- **Currently Checked-Out Branch:** `main`
- **App Python — Raiz da aplicação:** `aisstream_app`
- **Startup file:** `passenger_wsgi.py` · **Entrypoint:** `application`
- **Virtualenv:** `source /home/c62gtwye66po/virtualenv/aisstream_app/3.11/bin/activate && cd /home/c62gtwye66po/aisstream_app`

> ⚠️ **Atenção à estrutura aninhada:** no Git, os arquivos da app ficam em
> `aisstream_app/` (subpasta), ou seja `main.py` está em
> `/home/c62gtwye66po/aisstream_app/aisstream_app/main.py` após o clone. O
> `.cpanel.yml` precisa copiar do subdiretório correto para o `DEPLOYPATH` que
> o Passenger executa. Confirmar o caminho real no servidor antes de fixar.

---

## 2. Pré-requisitos no GitHub

1. Repositório `Jbvix/aisstream_app` acessível.
2. Branch de produção definida (hoje `main`). As features são desenvolvidas em
   branches `claude/...` e promovidas para `main` via merge/PR antes do deploy.
3. **Deploy key** (chave SSH) cadastrada para o cPanel puxar de repositório
   privado:
   - No cPanel: **Git Version Control** gera/usa a chave da conta.
   - No GitHub: **Settings → Deploy keys → Add deploy key** (cole a chave
     pública; *read-only* basta para pull).

---

## 3. Configurar o repositório no cPanel (primeira vez)

### Opção A — clonar do GitHub direto pelo cPanel
1. cPanel → **Git Version Control** → **Create**.
2. ✅ *Clone a Repository*.
3. **Clone URL:** `git@github.com:Jbvix/aisstream_app.git` (SSH, usando a deploy key)
   ou a URL HTTPS se for público.
4. **Repository Path:** `/home/c62gtwye66po/aisstream_app`.
5. **Create**. O cPanel clona e fica acompanhando o `origin`.

### Opção B — repositório já existe (caso atual)
Já existe o clone em `/home/c62gtwye66po/aisstream_app` apontando para `main`.
Basta usar **Manage → Pull or Deploy**.

---

## 4. Correção recomendada (resolver os bloqueios) — fazer ANTES do primeiro deploy automático

### 4.1 Parar de versionar arquivos de runtime
Mover os arquivos que a app reescreve para fora do controle de versão. Criar um
`.gitignore` (na raiz do repo) com:

```gitignore
# Dados gerados em runtime pela aplicação (não versionar — quebram o deploy do cPanel)
aisstream_app/data/users/*/saa_maneuvers.json
aisstream_app/data/users/*/tug_geofence_stats.json
aisstream_app/data/users/*/saa_schedule_monitor.json
aisstream_app/data/users/*/strategy_memory.json

# Logs e temporários
*.log
__pycache__/
*.pyc
.env
```

E remover do índice (mantendo no disco do servidor):

```bash
git rm --cached aisstream_app/data/users/default/saa_maneuvers.json \
                aisstream_app/data/users/default/tug_geofence_stats.json \
                aisstream_app/data/users/default/saa_schedule_monitor.json \
                aisstream_app/data/users/default/strategy_memory.json
git commit -m "Parar de versionar dados de runtime (evita working tree suja no cPanel)"
```

> `geofences.json` **continua versionado** (é configuração, não runtime).

### 4.2 Garantir um `.cpanel.yml` válido na raiz
Exemplo (ajustar `DEPLOYPATH` ao caminho real e à estrutura aninhada):

```yaml
---
deployment:
  tasks:
    - export DEPLOYPATH=/home/c62gtwye66po/aisstream_app
    # Copia os arquivos da app (subpasta aisstream_app/) para o DEPLOYPATH:
    - /bin/cp -R aisstream_app/. $DEPLOYPATH/
    # Reinício do app Python (Passenger): basta "tocar" o restart.txt:
    - /bin/mkdir -p $DEPLOYPATH/tmp
    - /bin/touch $DEPLOYPATH/tmp/restart.txt
```

> **Importante:** validar se o `DEPLOYPATH` deve receber o conteúdo da subpasta
> `aisstream_app/` (onde estão `passenger_wsgi.py` e `main.py`) e **não** a raiz
> do repo. Se a app já roda apontando para `/home/c62gtwye66po/aisstream_app`,
> os arquivos Python precisam aterrissar exatamente ali.

### 4.3 Instalar dependências no virtualenv (quando `requirements.txt` mudar)
O `.cpanel.yml` roda sem o virtualenv ativado; instalar dependências
manualmente após mudanças (ou via "Run Pip Install" na UI do app Python):

```bash
source /home/c62gtwye66po/virtualenv/aisstream_app/3.11/bin/activate
cd /home/c62gtwye66po/aisstream_app
pip install -r requirements.txt
```

> Nota: o `passenger_wsgi.py` importa `a2wsgi` — confirmar que está no
> `requirements.txt` do ambiente de produção (hoje lista apenas fastapi,
> uvicorn, python-dotenv, websockets, beautifulsoup4).

---

## 5. Fluxo de deploy do dia a dia

1. Desenvolver na branch de feature (`claude/...`), commitar e **push** para o GitHub.
2. Abrir/mergear PR para `main` (branch de produção).
3. No cPanel → **Git Version Control → Manage → Pull or Deploy**:
   - **Update from Remote** (puxa `main` do GitHub para o clone).
   - **Deploy HEAD Commit** (roda o `.cpanel.yml`).
4. Verificar:
   - App Python → **Reiniciar** (se o touch do restart.txt não bastar).
   - Abrir `https://tuglife.live/aisstream/` e conferir `/healthz` e `/api/status`.

---

## 6. Resolver "The system cannot deploy" / working tree suja

Se o deploy reclamar de arquivos modificados no servidor (Terminal cPanel/SSH):

```bash
cd /home/c62gtwye66po/aisstream_app
git status

# Backup dos dados de runtime, por segurança:
cp aisstream_app/data/users/default/saa_maneuvers.json /tmp/saa_maneuvers.bak 2>/dev/null
cp aisstream_app/data/users/default/tug_geofence_stats.json /tmp/tug_geofence_stats.bak 2>/dev/null

# Após aplicar o .gitignore da Seção 4, esses arquivos deixam de sujar a árvore.
# Se ainda estiverem tracked numa versão antiga, limpar:
git stash push -u -m "antes deploy cPanel"
```

Depois repetir **Update from Remote** + **Deploy HEAD Commit**.

---

## 7. Checklist de validação pós-deploy

- [ ] `GET https://tuglife.live/aisstream/healthz` responde `ok`.
- [ ] `GET /api/status` retorna o status esperado.
- [ ] Mapa ao vivo carrega e o WebSocket `/ws` conecta.
- [ ] Variáveis de ambiente presentes no app Python: `AISSTREAM_API_KEY`,
      `AIS_MODE=live`, `DEFAULT_AREA=rio`, `DASHBOARD_USER_ID=default`,
      `XAI_API_KEY`, `XAI_MODEL=grok-3-mini`.
- [ ] Worker AIS (long-running) sobreviveu ao restart do Passenger.

---

## 8. Boas práticas de segurança

- **Nunca** versionar `AISSTREAM_API_KEY` nem `XAI_API_KEY` — manter só como env
  vars no painel do app Python do cPanel (✅ já é o caso).
- Manter `.env` no `.gitignore`.
- Deploy key do GitHub em modo **read-only** para o cPanel.
