# Validação meteoceânica + variável Corrente

Autor: Jossian Brito

Data: 2026-06-15

## Pedido
Validar maré, vento e temperatura; incluir a variável **corrente** (em nós).

## Validação (antes)
- **Maré:** OK — Open-Meteo Marine `sea_level_height_msl` (nível, tendência,
  próxima virada), no front e no backend.
- **Temperatura:** OK no front (`temperature_2m`); **ausente** no contexto do
  KRATOS (backend).
- **Vento:** **BUG** — o front pedia `wind_speed_10m` (Open-Meteo entrega em
  **km/h**) e convertia com `toKnots` (×1,94384 = m/s→nós), **superestimando
  ~3,6×** (ex.: 12,9 km/h aparecia como 25,1 kn em vez de 7,0 kn).
- **Corrente:** inexistente.

## Correções
### Vento (bug)
- Front passa a pedir `&wind_speed_unit=kn` ao Open-Meteo e usa o valor direto
  (sem `toKnots`). Agora o vento exibido está correto em nós.

### Corrente (nova variável, em nós)
- **Backend** (`_fetch_tide_context`): adiciona `ocean_current_velocity` e
  `ocean_current_direction` ao Open-Meteo Marine; converte km/h→nós (÷1,852),
  direção em rosa-dos-ventos (`_compass_from_deg`). Retorna `current`,
  `currentSpeedKn`, `currentDirectionDeg`, `currentDirection`.
- **Backend** (`_fetch_metocean_context`): inclui `temperatureC`, `windSpeedKn`,
  `windDirection` (além de km/h) e os campos de corrente.
- **Insights do mapa**: nova linha de corrente; aviso quando ≥ 0,8 nó (acima de
  limites de manobra de vários terminais NPCP).
- **KRATOS**: prompt atualizado — considerar corrente e cruzar com os limites da
  NPCP-RJ (≤ 0,5 / 0,8 nó) na janela de manobra.
- **Frontend (mapa)**: novo **chip de corrente** no header e **linha "Corrente"**
  no painel de tempo; busca corrente no Open-Meteo Marine (km/h→nós) na hora de
  referência; painel/botão renomeados para "Tempo, maré, vento e corrente".

## Validações
- API conferida: `wind_speed_10m` = km/h (confirmado o bug); `ocean_current_*`
  disponível para a BG (0,3 km/h @ 45°).
- Backend (TestClient/local): metocean retorna temperatura 23 °C, vento 7 kn SO,
  maré 0,71 m subindo, **corrente 0,32 nós para NE**; insight de corrente gerado.
- `node --check` em index/dashboard e `ast.parse` em main → OK.

## Arquivos alterados
- `main.py` — corrente + temperatura no metocean, `_compass_from_deg`, insight,
  prompt, guia da interface.
- `frontend/index.html` — chip + painel de corrente, fetch de corrente, correção
  da unidade de vento (kn).
- `frontend/dashboard.html` — manual.
