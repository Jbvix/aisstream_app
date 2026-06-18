# Validação — alertas habilitados e ativos

Autor: Jossian Brito

Data: 2026-06-15

## Verificação
- **Tipos e padrões** (`ALERT_TYPES`): `barra`, `oportunidade`, `concorrente`,
  `fadiga` = **ligados por padrão**; `fleetOffline` = desligado. Preferências
  persistem em localStorage (`kratos.alertPrefs.v2`).
- **Guardas do disparo** (`fireAlert`): tipo habilitado + **armado** (8 s após o
  load) + **cooldown** de 10 min por (tipo+MMSI). Corretas.
- **Detecção** (`processVesselAlerts`): chamada a cada atualização de embarcação
  (no `upsertMarker`) e ao atualizar a programação. Saídas: toast + som (Web Audio)
  + notificação do navegador (se permitida) + histórico.
- **Pré-requisito de dados (backend):** navio dentro da BG recebe
  `geofencesInside: ['Baia de Guanabara Interno']`, que é o que `isInsideBarra`
  procura → **confirmado** por teste do `extract_normalized_vessel`.

## Correção de robustez
- **Risco encontrado:** toda a inicialização dos alertas/Orbe estava dentro do
  `.then(...)` da cadeia `loadAreas → … → setMode("live")`. Se qualquer passo
  falhasse, o `.catch` pulava a configuração → **alertas nunca armavam**.
- **Correção:** `setupAlertsPanel()`, `setupMobileUI()`, os timers
  (`refreshProgrammedNames`, `scanFleetOffline`, `refreshOperatingHours`) e o
  **aquecimento** (`_alertsArmed`) passaram para um `bootCoreUI()` executado
  **incondicionalmente**, independente das chamadas de dados.

## Como confirmar ao vivo
1. Abrir 🔔 (dock no desktop / barra no mobile): os tipos devem aparecer marcados.
2. Clicar **Testar** → toca som + mostra popup (confirma som/popup/permite áudio).
3. Os alertas reais são **por evento** (navio cruzando a barra, concorrente
   entrando, fadiga 7h/8h) — disparam quando o evento ocorre.

## Observações
- Som só toca após 1ª interação do usuário (regra do navegador) — abrir 🔔 /
  "Testar" resolve.
- `barra`/`oportunidade` exigem navio mercante (carga/petroleiro/passageiros) com
  LOA ≥ 120 m cruzando para dentro da BG.

## Arquivos alterados
- `frontend/index.html` — `bootCoreUI()` (init incondicional dos alertas/Orbe).
