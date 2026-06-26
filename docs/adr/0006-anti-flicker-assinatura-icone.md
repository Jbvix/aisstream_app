# ADR 0006 - Estabilidade dos alvos: recriar ícone só por "assinatura"

## Status
Aceito

## Contexto
Cada atualização AIS (polling ~0,8 s) recriava o `divIcon` do marcador (`setIcon`),
destruindo/recriando DOM → "piscar". Pior em alvos parados com heading ruidoso (511
→ COG aleatório) e com o anel de oportunidade pulsante em massa.

## Opções consideradas
- A) Recriar o ícone a cada atualização (estado original — pisca).
- B) Recriar só quando o visual muda de fato (assinatura) + estabilizar rumo.

## Decisão
B. `vesselIconSignature(v)` resume o que define o visual (categoria, rumo em passos,
movimento, SOG, frota/concorrente/oportunidade, zoom, dimensões). `setIcon` só roda
quando a assinatura muda; posição via `setLatLng` (não pisca). Rumo congela em
parado sem heading válido; rotação fora da assinatura quando o alvo é círculo;
acúmulo de horas usa delta de relógio global por MMSI (sem dupla contagem entre
streams). Anel de oportunidade fixo (sem pulsar) e só com programação carregada.

## Consequências
- (+) Alvos estáveis; menos repaint; CPU menor.
- (−) Lógica de assinatura precisa incluir todo novo fator visual (senão não
  re-renderiza). Documentado no código.

## Referências
`frontend/index.html` (`vesselIconSignature`, `upsertMarker`, `getIconRotationDegrees`),
relatórios `fix-piscar-anel-oportunidade`, `etapa-09`, `etapa-15`.
