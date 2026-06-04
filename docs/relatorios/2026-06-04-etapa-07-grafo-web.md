# Relatório de Etapa 07 — Grafo Estratégico nativo (Graph View web)

- **Data:** 2026-06-04
- **Branch de trabalho:** `claude/nifty-ride-Wj6RC`
- **Escopo:** trazer a visualização em grafo (estilo Obsidian) para dentro do
  KRATOS, em página própria, com botão de acesso.

---

## 1. Implementações (features novas)

| Área | Entrega |
|------|---------|
| Backend | `obsidian_notes.build_graph()` — nós/arestas do mesmo modelo das notas (Manobra ↔ Navio ↔ Berço ↔ Empresa ↔ Dia, Rebocador ↔ Empresa), com `group` por tipo e `val` por grau. |
| Backend | Endpoint `GET /api/obsidian/graph` (+ `/dashboard/api/...`) retorna `{nodes, links}`. |
| Backend | Rota `GET /graph` (+ `/graph/`) serve `frontend/graph.html`. |
| Frontend | Página `graph.html` — grafo de força via `force-graph` (CDN), cores por tipo iguais ao Graph View do Obsidian, rótulos ao dar zoom, clique para focar, botão atualizar, legenda e contador de nós/conexões. |
| Frontend | Botão **🕸️ Gráfico** no Dashboard (header) e **GR** no Mapa, com `href` resolvido pelo base path do app. |
| Manual | Nova entrada sobre o Grafo Estratégico + rodapé. |

## 2. Decisões de projeto

- **Reaproveitamento do modelo:** o grafo deriva da mesma fonte das notas
  (`build_dashboard_overview_dict` + frota), então a página web e o vault do
  Obsidian mostram exatamente a mesma rede.
- **Cores idênticas ao Obsidian** (verde SAAM, vermelho concorrente, azul navio,
  amarelo berço, roxo manobra, laranja empresa, cinza dia) para leitura
  consistente entre os dois ambientes.
- **Página estática + API:** `graph.html` é servido como arquivo e busca o JSON
  em `/api/obsidian/graph`, resolvendo o base path (sufixo `/graph`) igual ao
  padrão do dashboard — funciona sob o proxy `…/aisstream/`.
- **Sem dependência nova no backend:** só uma lib de front via CDN
  (`force-graph`), no mesmo padrão de Leaflet/Chart.js já usados.

## 3. Validações

- `ast.parse` em `main.py` e `obsidian_notes.py` — OK.
- Smoke-test do `build_graph` (2 manobras + frota): 13 nós / 11 conexões, grupos
  corretos — OK, sem rede.
- `node --check` nos scripts inline de `graph.html`, `dashboard.html` e
  `index.html` — OK.

## 4. Lições aprendidas

- Derivar a visualização web da **mesma função-fonte** das notas evita
  divergência entre o que o usuário vê no app e no Obsidian.
- `force-graph` entrega o visual "Obsidian" (pontos + arestas + rótulo no zoom)
  com poucas linhas, mantendo o padrão de libs via CDN do projeto.
