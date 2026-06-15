# Etapa 14 + 16 — Central de Alertas e Radar de oportunidade

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo

Implementar dois itens aprovados da reunião de 12/06:
- **Etapa 14 — Central de Alertas:** alertas sonoros + popup configuráveis no app,
  a pedido do usuário (ex.: entrada de navio na barra).
- **Etapa 16 — Radar de oportunidade:** navio entrando na barra **sem contrato**
  de reboque como alvo comercial. Decisões da aprovação: **LOA ≥ 120 m**, **apenas
  navios mercantes** (excluir offshore/PSV/AHTS).

## O que foi implementado

### Backend (`main.py`)
- Novo endpoint `GET /api/programmed-names`: nomes (normalizados) de **todos** os
  navios com manobra programada na Praticagem-RJ, de **qualquer empresa**
  (SAA/WIL/CAM). Base do radar de oportunidade (quem não consta = sem contrato).

### Frontend (`frontend/index.html`)
- **Motor de alertas** (`processVesselAlerts`) acionado a cada atualização AIS no
  `upsertMarker`:
  - detecta **cruzamento** para dentro da geofence da barra/BG (estado anterior →
    atual), evitando alertas repetidos;
  - **deduplicação** por (tipo + MMSI) com cooldown de 10 min;
  - **aquecimento** de 8 s no carregamento (não dispara "entrou" para quem já
    estava dentro no F5).
- **Tipos de alerta:** `barra` (entrada de navio), `oportunidade` (sem contrato),
  `concorrente` (WIL/CAM entrando na BG) e `fleetOffline` (rebocador sem sinal —
  desligado por padrão).
- **Saída ao usuário:** toast empilhável (cor por gravidade) com hora e botão
  **“Ver no mapa”** (usa `locateSaamVessel`); **som** via Web Audio (tons por
  gravidade, sem arquivos); **notificação do navegador** opcional (com pedido de
  permissão); badge no botão do dock; histórico recente.
- **Central 🔔** (novo botão no dock + painel flutuante): liga/desliga por tipo,
  som on/off + volume + testar, notificação on/off, lista de **oportunidades
  agora** e histórico. Preferências em `localStorage`.
- **Radar de oportunidade (Etapa 16):** navio com `shipCategory` ∈
  {carga, petroleiro, passageiros}, **não offshore** (exclui `rebocador_servico` e
  nomes PSV/AHTS/OSV/SUPPLY/OFFSHORE/FPSO…), **LOA ≥ 120 m**, dentro da barra e com
  nome **fora** da programação → marcado como oportunidade: **anel âmbar pulsante**
  no mapa (modo ícone e modo escala real) e item na lista da central. O flag entra
  na assinatura do ícone (`vesselIconSignature`) para re-render imediato.

### Documentação
- Manual do usuário (`dashboard.html`): seção “Central de Alertas (🔔) e
  oportunidades”.

## Decisões aplicadas
- LOA mínima do radar: **120 m**. Categorias-alvo: **navios mercantes**; offshore
  **excluído** por categoria e por heurística de nome.
- Janela da programação: usa o conjunto atual de manobras (a Praticagem mantém a
  janela operacional corrente).
- Cooldown de alerta: 10 min por (tipo + navio). Aquecimento: 8 s.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- `node --check` no script de `index.html` e `dashboard.html` → OK.
- TestClient: `GET /api/programmed-names` retorna nomes normalizados de todas as
  empresas (SAA/WIL/CAM), deduplicados, ignorando vazios.
- Consistência de IDs HTML×JS e funções únicas conferidas.

## Limitações / honestidade técnica
- **Oportunidade ≠ certeza:** o contrato pode existir e ainda não estar publicado
  na programação (falso positivo) — o rótulo é gatilho para verificação humana.
- **Geofence da barra:** a detecção usa a geofence "Baía de Guanabara Interno"
  (persistente) e nomes equivalentes ("barra"). Se quiser uma geofence específica
  só da barra de entrada, criamos no mapa e o motor passa a usá-la.
- **Som:** navegadores só tocam após 1ª interação do usuário (abrir a central /
  "Testar" resolve).
- **Alerta de concorrente** está vinculado à entrada na BG (não à geofence
  específica de manobra) — refino possível em etapa futura.

## Arquivos alterados
- `main.py` — endpoint `/api/programmed-names`.
- `frontend/index.html` — motor de alertas, central 🔔, anel de oportunidade, CSS.
- `frontend/dashboard.html` — Manual do usuário.
