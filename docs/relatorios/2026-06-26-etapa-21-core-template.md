# Etapa 21 — KRATOS Core (template reutilizável)

Autor: Jossian Brito
Data: 2026-06-26

## Objetivo
Materializar a estratégia de reuso decidida na Etapa 20 (ADR 0007): extrair a
fundação genérica do KRATOS para um **template** (`core-template/`) que sirva de
base a novos aplicativos, sem perder o raciocínio do projeto.

## Implementado
Pasta `core-template/` com esqueleto enxuto e executável:

- **`main.py`** — backend FastAPI genérico:
  - Acesso por convite (token): `create/revoke/validate`, middleware `access_gate`
    com tratamento de `root_path` (subcaminho), kill-switch `ACCESS_CONTROL`,
    chave-mestra `ADMIN_TOKEN`, cookie `kratos_access`.
  - APIs de acesso (`/api/access/*`) e admin de convites (`/api/admin/invites*`).
  - Relatório **PDF/DOCX** (`POST /api/report-file`) com `_report_sections()`
    marcado `TODO-DOMINIO`.
  - Health (`/healthz`, `/api/health`) e rotas de página (`/`, `/entrar`,
    `/admin`, `/versao`) + mount `/frontend`.
- **Frontend** (1 arquivo por página, tema escuro KRATOS):
  - `index.html` — shell com splash+progresso, header, barra inferior, orb,
    boot da UI fora da cadeia de dados, checagem de acesso e download de relatório.
  - `entrar.html` — validação de convite (suporta `?access=`).
  - `admin.html` — painel de convites (gerar/revogar/copiar link).
  - `versao.html` — painel de implementações.
  - `kratos-core.js` — helpers `KC.base/api/fetchJSON` (401→/entrar),
    **Central de Alertas** (Web Audio + popup centralizado + notificação + prefs)
    e **Dynamic Voice Orb** (placeholder).
- **Infra/deploy:** `requirements.txt`, `.env.example`, `.gitignore`,
  `passenger_wsgi.py` (a2wsgi ASGI→WSGI), `Procfile`.
- **Docs:** `README.md`, `CLAUDE.md` (modelo), `docs/CONTEXTO.md` (modelo),
  `docs/adr/README.md`, `docs/relatorios/README.md`.

Marcadores `TODO-DOMINIO` sinalizam exatamente o que reescrever por app.

## Validação
- `ast.parse(main.py)` OK.
- `node --check` OK em `kratos-core.js` e no JS inline de todas as páginas.

## Lições aprendidas
- Separar **genérico** (acesso, alertas, relatório, orb, subcaminho) do
  **específico** (domínio) deixa o ponto de partida de novos apps em minutos.
- Reaproveitar os padrões de robustez já provados (UI fora da cadeia de dados,
  401→login, `root_path` em redirects/cookies) evita repetir bugs antigos.

## Pendências / próximos passos
- Quando abrir o novo repositório, copiar `core-template/` como raiz e preencher
  os `TODO-DOMINIO` + `CLAUDE.md`/`CONTEXTO.md` do domínio.
- Etapa 17 — Corredores por GPX/XTE (aguardando arquivos de derrotas).
