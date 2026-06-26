# KRATOS Core — template reutilizável

Autor: Jossian Brito

Esqueleto (FastAPI + frontend estático) extraído do projeto **KRATOS** para
iniciar um **novo aplicativo** sem perder a fundação já testada. Traz os
recursos genéricos prontos; você implementa apenas o **domínio**.

> Base conceitual: ADR 0007 (estratégia de reuso multi-repo) do KRATOS.

## O que já vem pronto (genérico)
- Backend **FastAPI** servindo páginas estáticas (1 arquivo por página).
- **Acesso por convite** (token): `/entrar`, painel `/admin`, kill-switch
  `ACCESS_CONTROL`, chave-mestra `ADMIN_TOKEN`, cookie `kratos_access`.
- **Central de Alertas** (`KC.Alerts`): som por gravidade (Web Audio), popup
  centralizado, notificação, preferências por tipo.
- **Relatório PDF/DOCX** em `POST /api/report-file` (reportlab + python-docx).
- **Dynamic Voice Orb** (`KC.VoiceOrb`) — placeholder de assistente de voz.
- **Splash** com progresso + página `/versao`.
- Pronto para **subcaminho** (cPanel/Passenger/a2wsgi via `root_path`).
- Helpers de frontend em `frontend/kratos-core.js` (`KC.base/api/fetchJSON`,
  tratamento de 401 → `/entrar`).

## O que você implementa (domínio) — procure por `TODO-DOMINIO`
- `main.py`: fonte de dados e rotas específicas; `_report_sections()`.
- `frontend/index.html`: o conteúdo real da tela principal.
- `frontend/kratos-core.js`: disparar `KC.Alerts.fire(...)` nos eventos reais.

## Rodar local
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajuste APP_NAME / ADMIN_TOKEN / ACCESS_CONTROL
uvicorn main:app --reload     # http://127.0.0.1:8000
```

## Acesso por convite (resumo)
1. Defina `ADMIN_TOKEN` no `.env` e `ACCESS_CONTROL=on`.
2. Abra `/admin`, conecte com a chave e **gere um convite** (link `/entrar?access=…`).
3. O convidado abre o link uma vez; o cookie mantém o acesso no dispositivo.

Com `ACCESS_CONTROL=off` (padrão) o app fica aberto — útil em desenvolvimento.

## Deploy (cPanel + Passenger)
- `passenger_wsgi.py` faz a ponte ASGI→WSGI via `a2wsgi`.
- WSGI **não** suporta WebSocket → use polling se precisar de tempo real.
- App montado sob subcaminho; `root_path` já é tratado em redirects/cookies.

## Convenções de trabalho
Veja `CLAUDE.md`, `docs/CONTEXTO.md` e os modelos em `docs/adr/` e
`docs/relatorios/`. Mantenha **ADRs + relatórios** desde o 1º dia.

## Estrutura
```
core-template/
├── main.py                 # backend (genérico) — TODO-DOMINIO marca o que trocar
├── passenger_wsgi.py       # entrada cPanel/Passenger
├── Procfile                # dev/hosts PaaS
├── requirements.txt
├── .env.example
├── frontend/
│   ├── index.html          # shell: splash, header, barra inferior, orb
│   ├── entrar.html         # tela de convite
│   ├── admin.html          # painel de convites
│   ├── versao.html         # implementações
│   └── kratos-core.js      # helpers: API, alertas, orb
└── docs/
    ├── CONTEXTO.md         # context pack (modelo)
    ├── adr/README.md       # template de ADR
    └── relatorios/README.md
```
