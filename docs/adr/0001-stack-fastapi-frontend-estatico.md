# ADR 0001 - Stack: FastAPI + frontend estático, arquivo único por página

## Status
Aceito

## Contexto
App de monitoramento AIS com mapa ao vivo, painel e assistente, hospedado em
cPanel compartilhado (sem Docker/Node server). Precisa ser simples de implantar
(git pull) e de baixo custo operacional.

## Opções consideradas
- A) SPA (React/Vue) + API separada.
- B) FastAPI servindo HTML estático auto-contido (1 arquivo por página, JS inline).
- C) Framework full-stack (Django, etc.).

## Decisão
B. Backend FastAPI em `main.py` (flat) + páginas estáticas em `frontend/`
(`index.html`, `dashboard.html`, `graph.html`…), cada uma auto-contida (CSS/JS
inline, libs via CDN: Leaflet, Chart.js). Leitura/edição direta, sem build step.

## Consequências
- (+) Deploy trivial (git pull + restart), zero pipeline de build, fácil de auditar.
- (+) Validação simples: `ast.parse` no Python e `node --check` no script do HTML.
- (−) Arquivos grandes (index.html ~5k linhas) e algum CSS/JS repetido entre páginas.
- (−) Sem tree-shaking/minificação; mitigado pelo escopo enxuto.

## Referências
`main.py`, `frontend/*.html`, `docs/ARQUITETURA_E_IMPLANTACAO.md`, `CLAUDE.md`.
