# Etapa 09 — Alvos em escala real (estilo MarineTraffic)

Autor: Jossian Brito

Data: 2026-06-12

## Objetivo

Aproximar a representação dos alvos no mapa ao vivo do visual do MarineTraffic:
mostrar os navios atracados deitados sobre o cais, respeitando o **zoom** e as
**dimensões reais** das embarcações — em vez de ícones de tamanho fixo que não
casam com a pegada real da embarcação sobre a imagem de satélite.

## O que foi implementado

### Backend (`main.py`)
- Nova função `extract_ship_ref_offsets(message_type, message_body)`: extrai do
  AIS os offsets do ponto de referência (antena) ao casco — **A/B/C/D** em metros
  (A = proa, B = popa, C = bombordo, D = boreste). LOA = A+B, Boca = C+D. Já
  havia a leitura de dimensões, mas os offsets de referência eram descartados.
- Os offsets passam a ser **cacheados** por MMSI (`refOffsets`) junto às demais
  dimensões e incluídos no payload de cada embarcação como `refToBow`,
  `refToStern`, `refToPort`, `refToStarboard`. Validação: LOA ≤ 600 m, boca ≤ 120 m.

### Frontend (`frontend/index.html`)
- **Modo escala real**: a partir do zoom `TRUE_SCALE_MIN_ZOOM = 14` (e quando o
  casco renderiza ≥ `TRUE_SCALE_MIN_PX = 16 px`), as embarcações deixam de ser
  ícones de tamanho fixo e passam a ser desenhadas como o casco em **escala
  geográfica real**.
- `metersPerPixel(lat, zoom)`: metros por pixel no Web Mercator para converter as
  dimensões em metros para pixels no zoom corrente.
- `buildVesselHullPath(w, h)`: silhueta de navio (proa pontuda, costados retos,
  popa reta) — substitui o dardo simples quando em escala real.
- `buildTrueScaleIcon(...)`: monta o `divIcon` com o casco posicionado de forma
  **absoluta** dentro de um wrap quadrado centrado na **antena AIS**; o wrap gira
  pelo rumo (`transform-origin` no centro = antena), então o ponto permanece sobre
  a posição mesmo com a embarcação atracada/girada. Quando há A/B/C/D, o casco é
  ancorado no ponto real da antena; sem eles, usa LOA/boca centradas.
- O ramo de escala real foi inserido em `createVesselIcon`/`iconForVessel`,
  preservando o modo ícone-seta para zoom afastado. O handler `zoomend` já
  recalculava os ícones, então a transição entre os dois modos é automática.
- CSS: classe `ship-true` para o casco alongado — suprime o anel arredondado do
  SAAM (que viraria elipse) e ajusta o contorno de concorrentes (vermelho).

## Comportamento resultante
- Zoom afastado: ícones-seta de sempre, legíveis de longe.
- Zoom aproximado (~14+): navio atracado fica deitado sobre o cais, no tamanho
  certo e alinhado ao rumo — como no MarineTraffic.
- Embarcações pequenas (rebocadores) só viram casco quando o zoom é alto o
  bastante para render ≥ 16 px, evitando slivers ilegíveis.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- `node --check` no bloco de script do `index.html` → OK.
- Prova visual estática da silhueta e da ancoragem na antena (proa pontuda,
  costados retos, popa reta; atracados alinhados ao cais girando em torno do
  ponto da antena).

## Lições aprendidas
- Para ancoragem geográfica correta com rotação CSS, o caminho robusto é **centrar
  o ponto de âncora (antena) no centro do wrap** e girar em torno dele; assim o
  `iconAnchor` é o centro e a posição AIS não "desliza" ao rotacionar.
- O AIS já trazia A/B/C/D; bastava parar de descartá-los para habilitar a
  ancoragem realista do casco no cais.

## Arquivos alterados
- `main.py` — extração/cache/payload dos offsets de referência (A/B/C/D).
- `frontend/index.html` — modo escala real (helpers, `buildTrueScaleIcon`, CSS).
- `frontend/dashboard.html` — Manual do usuário atualizado (seção "No mapa ao vivo").
