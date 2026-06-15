# Etapa 15 — Horímetro de operação do rebocador (controle de fadiga)

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo

Controlar as horas de operação de cada rebocador para prevenção de fadiga, com
limite de **8 h**, conforme a interpretação definida pelo usuário.

## Interpretação aprovada (reunião / 15-06)
- **Repouso** = rebocador atracado, MCPs parados (no AIS: parado/SOG baixo).
- **Operação** = qualquer movimento — **manobra OU deslocamento** de um ponto a
  outro — é contabilizado.
- Após **8 h de operação**, o rebocador entra em **recuperação de fadiga**;
  **8 h de repouso contínuo** zeram a fadiga (revezamento).

## O que foi implementado

### Backend (`main.py`)
- `update_saam_operating_hours(vessel)` — acumulador por rebocador SAAM, chamado no
  ponto único de processamento AIS (`extract_normalized_vessel`). Usa o **delta de
  relógio global por MMSI** (robusto contra dupla contagem entre múltiplos streams);
  lacunas > 10 min (sinal perdido) não contam.
  - **Movimento** (SOG ≥ 0,5 kn) acumula `operatingSec` e zera `restingSec`;
  - **Parado** acumula `restingSec`; ao atingir **8 h** de repouso contínuo,
    `operatingSec` é zerado (recuperado);
  - histórico por dia (`byDay`, 30 dias) para relatório.
- Persistência em `tug_geofence_stats.json` (chave `operating`), salvando ao cruzar
  marco (7 h/8 h) ou a cada ~2 min.
- Constantes configuráveis por env: `TUG_OP_LIMIT_HOURS` (8), `TUG_OP_WARN_HOURS`
  (7), `TUG_RECOVERY_HOURS` (8).
- Endpoint `GET /api/saam-operating-hours` (config + linhas por rebocador com
  `operatingHours`, `restingHours`, `moving`, `recovered`, `status`).
- Contexto do KRATOS: `tugOperatingHours` + instrução no system prompt para
  **evitar rebocadores em atenção/limite** na recomendação de alocação.

### Frontend (`frontend/index.html`)
- Polling de `/api/saam-operating-hours` (60 s).
- **Barra de operação** por rebocador no painel SAAM-BGRA (verde/âmbar/vermelho,
  horas do dia, “operando/recuperado”).
- **Alerta de fadiga** integrado à Central de Alertas (Etapa 14): dispara em **7 h**
  (atenção) e **8 h** (limite), com dedup por nível/dia; rearma ao recuperar.

### Documentação
- Manual do usuário: seção “Controle de horas de operação (fadiga)”.
- Proposta: Etapa 15 marcada como concluída.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK; `node --check`
  no `index.html` → OK.
- Acumulador (passos dentro do cap): ~8,2 h → status **limite**; 8 h parado →
  **recuperado** (zera); ~7,1 h → **atenção**; lacuna > 10 min não conta.
- Endpoint testado (TestClient): 7,5 h → status “atencao”.

## Observações / limitações
- A operação é inferida do **SOG** (não há leitura de MCP via AIS). Espera curta
  alongside (SOG ~0) conta como repouso, mas só **8 h** contínuas zeram a fadiga —
  pausas entre fainas não reiniciam o ciclo. Conservador e fiel à intenção.
- O ciclo de fadiga é **contínuo** (baseado em repouso), não reinicia à meia-noite;
  há histórico por dia para relatório.

## Arquivos alterados
- `main.py` — acumulador, endpoint, contexto/prompt do KRATOS, constantes.
- `frontend/index.html` — polling, barra de operação no painel SAAM, alerta de fadiga.
- `frontend/dashboard.html` — Manual do usuário.
