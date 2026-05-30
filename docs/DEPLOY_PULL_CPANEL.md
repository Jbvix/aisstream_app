# Pull / Deploy GitHub → cPanel

Guia operacional do fluxo de deploy da aplicação hospedada no cPanel
(`https://tuglife.live/aisstream/`), puxando do GitHub (`Jbvix/aisstream_app`).

> **Status:** ✅ Pipeline **configurado e conectado** (reconciliação feita em
> 2026-05-30). O `main` do GitHub passou a ser a fonte da verdade, com o
> histórico real e estrutura **flat**.

---

## 1. Topologia real (confirmada no servidor)

| Item | Realidade |
|---|---|
| **Clone Git = app viva** | `/home/c62gtwye66po/aisstream_app` — a aplicação **roda direto do clone** (estrutura *flat*: `main.py`, `passenger_wsgi.py` na raiz). |
| **`.cpanel.yml`** | `DEPLOYPATH` = o próprio clone; a tarefa de deploy apenas garante `tmp/` e `frontend/` e dá `touch tmp/restart.txt` (reinicia o Passenger no lugar). |
| **`.gitignore`** | Já ignora os arquivos de runtime que sujavam a árvore (`data/users/default/saa_maneuvers.json`, `tug_geofence_stats.json`, `saa_schedule_monitor.json`, `strategy_memory.json`), `tmp/`, `__pycache__/`, `.env`, `aisstream-example/`. |
| **`origin`** | Aponta para **GitHub** (`https://github.com/Jbvix/aisstream_app.git`). O antigo remote SSH self-referencial foi renomeado para `cpanel-ssh`. |
| **`public_html/aisstream_app`** | É uma **cópia** antiga (não é a app viva). Pode ser limpa quando conveniente. |
| **App Python** | Raiz `aisstream_app`, startup `passenger_wsgi.py`, entrypoint `application`, virtualenv Python 3.11. |

Fluxo final:

```
edita → commit → push GitHub (main) → cPanel "Update from Remote" → "Deploy HEAD Commit" → touch restart.txt → produção
```

---

## 2. Como foi feita a reconciliação (registro histórico)

O GitHub era novo (criado em 30/05) e tinha só um `main` descartável nested
(*"Add files via upload"*), enquanto o histórico real (flat) vivia apenas no
clone do cPanel. Passos executados **no servidor**:

```bash
cd /home/c62gtwye66po/aisstream_app
git status                       # working tree clean
# Publica o app real (flat) no GitHub, sobrescrevendo o main descartável:
git push https://<TOKEN>@github.com/Jbvix/aisstream_app.git main:main --force
# Reaponta o clone para puxar do GitHub no futuro:
git remote rename origin cpanel-ssh
git remote add origin https://github.com/Jbvix/aisstream_app.git
git fetch origin
git branch --set-upstream-to=origin/main main
```

> O token usado foi **revogado** após o push (repo público → pulls não precisam de credencial).

---

## 3. Deploy do dia a dia

1. Desenvolver na branch de feature (`claude/...`), commitar e **push** ao GitHub.
2. Mergear para `main` (via PR ou merge direto).
3. cPanel → **Git Version Control → Manage → Pull or Deploy**:
   - **Update from Remote** → puxa o `main` do GitHub para o clone.
   - **Deploy HEAD Commit** → roda o `.cpanel.yml` (touch `restart.txt`).
4. Se necessário, **Reiniciar** o app na tela do Python App.

> Como a árvore de runtime já está no `.gitignore`, o "Update from Remote"
> normalmente não esbarra em *working tree suja*. Se esbarrar, ver Seção 5.

---

## 4. Quando `requirements.txt` mudar

O `.cpanel.yml` não ativa o virtualenv. Após alterar dependências:

```bash
source /home/c62gtwye66po/virtualenv/aisstream_app/3.11/bin/activate
cd /home/c62gtwye66po/aisstream_app
pip install -r requirements.txt
```

> Conferir que `a2wsgi` (usado em `passenger_wsgi.py`) está disponível no
> ambiente — não consta no `requirements.txt` atual (fastapi, uvicorn,
> python-dotenv, websockets, beautifulsoup4).

---

## 5. "The system cannot deploy" / working tree suja

Se o pull/deploy reclamar de arquivos modificados no servidor:

```bash
cd /home/c62gtwye66po/aisstream_app
git status
# Backup, por segurança:
cp data/users/default/saa_maneuvers.json /tmp/saa_maneuvers.bak 2>/dev/null
# Guardar e voltar ao HEAD limpo:
git stash push -u -m "antes do deploy"
```

Depois repetir **Update from Remote** + **Deploy HEAD Commit**.

---

## 6. Checklist de validação pós-deploy

- [ ] `GET https://tuglife.live/aisstream/healthz` responde ok.
- [ ] `GET /api/status` retorna o status esperado.
- [ ] Mapa ao vivo carrega (em produção usa *polling* quando o WSS falha).
- [ ] Env vars presentes: `AISSTREAM_API_KEY`, `AIS_MODE=live`,
      `DEFAULT_AREA=rio`, `DASHBOARD_USER_ID=default`, `XAI_API_KEY`,
      `XAI_MODEL=grok-3-mini`.

---

## 7. Segurança

- **Nunca** versionar `AISSTREAM_API_KEY` / `XAI_API_KEY` — só como env vars no cPanel.
- `.env` está no `.gitignore`.
- Para pushes a partir do servidor, usar token efêmero (revogar após uso) ou
  configurar uma *deploy key* SSH com escrita.
