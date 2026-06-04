# Relatório de Etapa 02 — Integração Obsidian (Sprint 1: Exportador Base)

- **Data:** 2026-06-04
- **Branch de trabalho:** `claude/nifty-ride-Wj6RC`
- **Baseline:** `b4eb59f`
- **Escopo:** Sprint 1 da proposta `docs/PROPOSTA_OBSIDIAN_KRATOS.md`
  (Conexão com Supabase Storage + Exportador Base).

Primeira etapa da ponte **KRATOS → Supabase Storage → Obsidian (Remotely Save)**.
Objetivo: o backend no cPanel conseguir gerar e subir notas Markdown para um
bucket privado, com diagnóstico e teste de conexão.

---

## 1. Implementações (features novas)

| Área | Entrega |
|------|---------|
| Backend | Módulo `obsidian_supabase.py` — config via env, `upload_note`, `build_note` (frontmatter YAML), `check_connection` e wrappers async. |
| Backend | Endpoints `GET /api/obsidian/status` (diagnóstico sem segredos) e `POST /api/obsidian/test-upload` (sobe nota de saúde no bucket). Espelhados sob `/dashboard/api/...`. |
| Config | `.env.example` versionado documentando `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET`, `OBSIDIAN_NOTE_PREFIX` e as chaves S3 (consumidas pelo Obsidian). |
| Docs | Proposta versionada em `docs/PROPOSTA_OBSIDIAN_KRATOS.md`. |

## 2. Decisões de projeto

- **Zero dependências novas:** upload via **REST API de Storage do Supabase**
  usando apenas `urllib` (stdlib), em vez de `boto3`. O deploy é em cPanel, onde
  instalar pacotes é frágil; o `requirements.txt` permanece intacto.
- **Backend usa REST (Bearer), não S3.** As chaves `SUPABASE_S3_*` servem só ao
  plugin Remotely Save no lado do Obsidian; ficam documentadas no `.env` para o
  tutorial (Sprint 4), mas o backend não as usa.
- **Prefixo dedicado (`kratos/`)** para as notas geradas, separado das notas
  livres do usuário — evita que o sincronismo bidirecional do Remotely Save
  sobrescreva edições manuais.
- **Upload assíncrono** (`asyncio.to_thread`) seguindo o padrão já usado no sync
  da Praticagem, para não bloquear o relay AIS.

## 3. Validações

- `python3 -c "import ast; ast.parse(...)"` em `main.py` e `obsidian_supabase.py` — OK.
- Smoke-test do módulo: `config_status()` e `build_note()` (frontmatter com
  escape de `:` em valores) — OK.

## 4. Pendências / próximas sprints

- **Sprint 2:** notas ricas interligadas (Manobra ↔ Navio ↔ Berço ↔ Rebocador ↔
  Dia) com tags `#kratos/...` e maré/vento reais.
- **Sprint 3:** gatilho automático no loop async + botão no Dashboard
  (**aqui o Manual do usuário será atualizado**, pois passa a haver comportamento
  visível — conforme regra 1 do CLAUDE.md).
- **Sprint 4:** tutorial Remotely Save + Graph View.

## 5. Lições aprendidas

- Preferir stdlib (`urllib`) a `boto3` reduz risco de deploy no cPanel sem perder
  capacidade — a REST API de Storage cobre o caso de upload de notas.
- Separar **notas geradas** de **notas do usuário** desde a Sprint 1 evita perda
  de dados quando o Remotely Save (bidirecional) entrar em cena.
