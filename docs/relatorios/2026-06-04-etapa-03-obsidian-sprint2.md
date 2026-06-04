# Relatório de Etapa 03 — Integração Obsidian (Sprint 2: Motor de Links & Grafos)

- **Data:** 2026-06-04
- **Branch de trabalho:** `claude/nifty-ride-Wj6RC`
- **Escopo:** Sprint 2 da proposta `docs/PROPOSTA_OBSIDIAN_KRATOS.md`
  (notas ricas interligadas + tags estruturadas + maré/vento reais).

Constrói o **grafo de conhecimento** do KRATOS: a partir do estado ao vivo
(manobras da Praticagem, AIS, geofences, market share, maré/vento) gera um
conjunto de notas Markdown com backlinks `[[...]]` e tags.

---

## 1. Implementações (features novas)

| Área | Entrega |
|------|---------|
| Backend | Módulo `obsidian_notes.py` — motor puro/testável que modela as notas. |
| Modelo | Notas interligadas: **Manobra ↔ Navio ↔ Berço ↔ Rebocador ↔ Dia ↔ Empresa**. |
| Tags | `#kratos/manobra[/saam\|/concorrente]`, `#kratos/navio/comercial`, `#kratos/berço`, `#kratos/rebocador/{saam,concorrente}`, `#kratos/empresa/{saam,concorrente}`, `#kratos/dia`. |
| Meteocean | Nota **Condição Diária** integra **vento e maré reais** (Open-Meteo) na nota do dia corrente. |
| Rebocadores | Notas com **SOG/COG** e base/geofence atual (frota SAAM por MMSI + concorrentes WIL/CAM). |
| Backend | `obsidian_supabase.upload_notes()` — upload de lote tolerante a falha. |
| Backend | Endpoint `POST /api/obsidian/export` (e `/dashboard/api/...`) gera e sobe o vault. |
| Backend | Mapa `SAAM_BGRA_NAMES` (MMSI → nome) para nomes estáveis dos rebocadores. |

## 2. Decisões de projeto

- **Links por basename.** Nome de exibição de cada entidade é usado como título,
  arquivo **e** alvo de `[[link]]`, passando pelo mesmo sanitizador (`_fname`),
  garantindo que as arestas do grafo fechem mesmo com `/`, `:` etc. nos nomes.
- **Módulo puro:** `obsidian_notes` não importa `main`; recebe os dados como
  argumentos (overview, vessels, metocean, frotas). Testável isoladamente.
- **Maré/vento só na nota de hoje:** são valores instantâneos; aplicá-los a dias
  passados seria incorreto.
- **SAA = SAAM** respeitado em todas as tags e rótulos (`saam` vs `concorrente`).
- **Prefixo `kratos/`** continua sendo a única fonte do caminho (resolvido no
  `upload_note`); o gerador devolve caminhos relativos.

## 3. Validações

- `ast.parse` em `main.py`, `obsidian_notes.py`, `obsidian_supabase.py` — OK.
- Smoke-test do `build_vault` com dados sintéticos (2 manobras, frota + 2
  concorrentes, metocean) → 14 notas coerentes; links de Manobra/Dia conferem
  com os arquivos de Navio/Berço/Empresa. Sem chamadas de rede.

## 4. Pendências / próximas sprints

- **Sprint 3:** gatilho automático (loop async, com **debounce**) + botão
  **"Sincronizar Obsidian"** no Dashboard. **Aqui o Manual do usuário será
  atualizado** (primeiro comportamento visível ao usuário), conforme regra 1.
- **Sprint 4:** tutorial Remotely Save + cores do Graph View.

## 5. Lições aprendidas

- Centralizar a sanitização de nomes num único `_fname` é o que mantém o grafo
  íntegro — link e arquivo nunca divergem.
- Separar **modelagem** (`obsidian_notes`) de **transporte** (`obsidian_supabase`)
  deixou cada peça pequena e testável, espelhando as seções 1 e 2 da proposta.
