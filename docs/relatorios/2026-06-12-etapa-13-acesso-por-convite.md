# Etapa 13 — Acesso ao app por convite (token via WhatsApp/e-mail)

Autor: Jossian Brito

Data: 2026-06-12

## Objetivo

Implementar, a partir da página do administrador, um sistema de **tokens de acesso
ao app** com **convite por WhatsApp / e-mail**. Decisões do usuário:
- **Escopo:** o app inteiro (mapa + painel) passa a ser **só por convite**.
- **Envio:** **links prontos** (`wa.me` + `mailto`) — sem SMTP no servidor.
- **Controles:** revogar a qualquer momento, validade/expiração e rótulo por
  convidado + registro de último acesso.

## O que foi implementado

### Backend (`main.py`)
- **Núcleo de convites** (armazenado em `data/users/<id>/access_invites.json`,
  gitignored): criar (`secrets.token_urlsafe`), listar, revogar, validar e
  registrar último acesso (throttle de 1×/min por token). Cada convite tem
  rótulo, criação, expiração opcional, revogado, último acesso e contador.
- **Middleware `access_gate_middleware`**: quando `ACCESS_CONTROL=on`, exige token
  válido (cookie `kratos_access`, `?access=` ou cabeçalho `X-Access-Token`) para
  tudo, **exceto** `/entrar`, `/api/access/*`, `/admin`, `/api/admin/*` e estáticos.
  Sem token → páginas redirecionam a `/entrar`; APIs retornam 401. O link de
  convite (`?access=`) grava o cookie de sessão (HttpOnly, SameSite=Lax, Secure
  quando HTTPS). **`ADMIN_TOKEN` é chave-mestra** (nunca há lockout do dono).
- **APIs públicas:** `GET /api/access/status`, `POST /api/access/validate`
  (grava cookie), `POST /api/access/logout`. Página `GET /entrar`.
- **APIs do admin** (exigem `ADMIN_TOKEN`): `GET/POST /api/admin/invites`,
  `POST /api/admin/invites/revoke`.
- **Kill-switch seguro:** `ACCESS_CONTROL` desligado por padrão — o deploy do
  código **não tranca** o site; a trava só entra ao definir `ACCESS_CONTROL=on`.

### Frontend
- **`frontend/entrar.html`** (novo): porta de entrada com identidade KRATOS. Lê
  `?c=<token>` do link e entra sozinho; ou permite colar o token. Mensagens de
  erro para convite inválido/expirado/revogado.
- **`frontend/admin.html`**: nova aba **Convites de acesso** — formulário (rótulo
  + validade), tabela com status/validade/último acesso e, por convite, botões
  **WhatsApp** (`wa.me` preenchido), **E-mail** (`mailto:` preenchido), **Copiar
  link** e **Revogar**. Mostra o estado do `ACCESS_CONTROL` e instruções.

### Documentação
- `docs/PAGINA_ADMIN.md`: seção “Convites de acesso” (uso, ativação, endpoints,
  limitações).
- Manual do usuário (`dashboard.html`): bloco “Acesso por convite (token)”.
- `.gitignore`: `data/users/*/access_invites.json` (contém segredos).

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- `node --check` em `entrar.html`, `admin.html`, `dashboard.html` → OK.
- Testes de lógica: criar/validar/revogar/expirar e isenções de rota → OK.
- Testes de integração (TestClient): `/` sem token → 307 `/entrar`; API sem token
  → 401; `/entrar` e `/admin` abertos; `?access=` libera e grava cookie; validate
  + cookie navega; chave-mestra entra; token inválido recusado; admin
  cria/lista/revoga e exige `ADMIN_TOKEN` (401 sem ele).

## Como ativar (servidor cPanel)
1. `git pull origin main && touch tmp/restart.txt`.
2. Garanta `ADMIN_TOKEN` definido (já usado pela página admin).
3. Gere convites na aba *Convites de acesso* e teste um link.
4. Defina `ACCESS_CONTROL=on` (Setup Python App → Environment) e reinicie.

## Limitações / evolução futura
- O **WebSocket** de dados AIS não é coberto pela trava HTTP (apenas páginas e
  APIs REST). Gating do WS pode ser adicionado se necessário.
- Sem SMTP: o envio parte do aparelho/cliente do admin (links prontos). Envio
  automático por e-mail exigiria configurar SMTP (decisão adiada).

## Arquivos alterados
- `main.py` — núcleo de convites, middleware de gate, APIs de acesso e de admin.
- `frontend/entrar.html` (novo) — porta de entrada.
- `frontend/admin.html` — aba Convites de acesso.
- `frontend/dashboard.html` — manual.
- `docs/PAGINA_ADMIN.md`, `.gitignore`.
