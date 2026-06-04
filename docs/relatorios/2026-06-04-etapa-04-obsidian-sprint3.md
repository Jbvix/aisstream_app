# Relatório de Etapa 04 — Integração Obsidian (Sprint 3: Automação no cPanel)

- **Data:** 2026-06-04
- **Branch de trabalho:** `claude/nifty-ride-Wj6RC`
- **Escopo:** Sprint 3 da proposta `docs/PROPOSTA_OBSIDIAN_KRATOS.md`
  (gatilho automático + botão no Dashboard).

Automatiza o envio das notas e expõe o controle no painel — **primeiro
comportamento visível ao usuário** da integração.

---

## 1. Implementações (features novas)

| Área | Entrega |
|------|---------|
| Backend | Loop assíncrono `_obsidian_auto_sync_loop` (no event loop do FastAPI, padrão Passenger-safe), iniciado/cancelado no `startup`/`shutdown`. |
| Backend | Gatilho **após cada sync da Praticagem** (`_obsidian_auto_export_if_due`). |
| Backend | **Debounce** por intervalo mínimo (`OBSIDIAN_AUTO_SYNC_SECONDS`, padrão 300 s) — evita upload a cada posição AIS. Guarda de reentrância (`_obsidian_export_running`). |
| Backend | `/api/obsidian/status` agora reporta `autoSync`, `autoSyncSeconds`, `lastExportTs`. |
| Frontend | Seção **“Integração Obsidian (Supabase)”** com botão **“Sincronizar Obsidian”**, mensagem de resultado e linha de estado (bucket/prefixo/auto). |
| Manual | Nova seção no Manual do usuário + rodapé de “última atualização”. |
| Config | `OBSIDIAN_AUTO_SYNC` e `OBSIDIAN_AUTO_SYNC_SECONDS` no `.env.example`. |

## 2. Decisões de projeto

- **Gatilho no loop async existente**, não em processo separado: o cPanel
  (Passenger) recicla workers; seguir o mesmo padrão do `_praticagem_auto_sync_loop`
  é o caminho seguro.
- **Tolerante a falha:** o auto-export nunca propaga exceção para o relay AIS nem
  para a resposta do sync da Praticagem (try/except + swallow + log implícito).
- **Debounce único:** tanto o loop periódico quanto o gatilho pós-Praticagem usam
  a mesma checagem de janela mínima e o mesmo timestamp, então não há export
  duplicado. O botão manual e o auto-export atualizam o mesmo `lastExportTs`.
- **Off por padrão:** `OBSIDIAN_AUTO_SYNC=0` — a automação só liga por opção
  explícita no servidor; o botão manual funciona independentemente.

## 3. Validações

- `ast.parse` em `main.py` — OK.
- `node --check` no `<script>` do `dashboard.html` (26 KB) — OK.
- Módulos `obsidian_*` importam e geram notas sem rede (Sprint 2) — OK.
- Observação: `fastapi` não está instalado neste ambiente de CI, então o import
  de `main` não roda aqui; a validação é por `ast.parse` (conforme regra 2).

## 4. Pendências / próximas sprints

- **Sprint 4:** tutorial de configuração do Remotely Save + cores do Graph View
  (homologação final). Já documentado parcialmente na proposta (seção 4).

## 5. Lições aprendidas

- Reaproveitar o padrão de task de fundo já existente (Praticagem) reduziu o
  risco no cPanel e manteve o `startup`/`shutdown` coerentes.
- Centralizar debounce + timestamp num único caminho evita corrida entre o
  gatilho periódico, o pós-Praticagem e o botão manual.
