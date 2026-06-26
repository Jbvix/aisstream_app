# Etapa 20 — Preservação de raciocínio: CONTEXTO, ADRs e reúso multi-repo

Autor: Jossian Brito

Data: 2026-06-26

## Objetivo
Garantir que o raciocínio e a lógica do projeto não se percam ao iniciar novos
aplicativos (novos repositórios) e ao reidratar sessões de IA.

## O que foi criado
- **`docs/CONTEXTO.md`** — context pack: o que é, stack/topologia, decisões-chave
  (com links aos ADRs), convenções, o que está pronto, pendências, glossário do
  domínio e guia para iniciar um novo app.
- **ADRs retroativos** em `docs/adr/` (decisões maiores já tomadas):
  - 0001 — Stack FastAPI + frontend estático (1 arquivo/página).
  - 0002 — Polling vs WebSocket (Passenger/WSGI não faz WS).
  - 0003 — Subcaminho `/aisstream` (root_path em redirects/cookies/links).
  - 0004 — Acesso por convite (token), kill-switch e chave-mestra.
  - 0005 — Conhecimento NPCP-RJ embutido no prompt, foco BG.
  - 0006 — Anti-flicker: recriar ícone só por "assinatura".
  - 0007 — Estratégia de reúso multi-repo (template → lib).
- **`docs/STARTER_NOVO_APP.md`** — passo a passo + modelo de `CLAUDE.md` +
  checklist genérico × específico para abrir um novo repositório reaproveitando a
  fundação ("KRATOS Core").

## Como usar
- Nova sessão de IA: "Leia `docs/CONTEXTO.md`, os ADRs em `docs/adr/` e os
  relatórios recentes antes de começar."
- Novo app: criar repo (template), copiar `CLAUDE.md` + `docs/CONTEXTO.md` próprios,
  manter ADRs + relatórios desde o 1º commit.

## Arquivos criados
- `docs/CONTEXTO.md`
- `docs/adr/0001..0007-*.md`
- `docs/STARTER_NOVO_APP.md`
- este relatório
