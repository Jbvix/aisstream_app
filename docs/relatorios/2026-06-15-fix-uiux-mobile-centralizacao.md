# Correção UI/UX mobile — centralização (mapa, alertas, ícones do topo)

Autor: Jossian Brito

Data: 2026-06-15

## Validação do print
- **Mapa deslocado/com margens e cantos:** `.map-wrap` mantinha `left: var(--dock-w)`
  (deslocamento da largura do dock, mesmo com o dock oculto no celular) e `padding`;
  `#map` tinha `border-radius`/borda/sombra → mapa não ocupava a tela e ficava
  "encaixotado".
- **Header alto e desalinhado:** os 3 grupos (título, lâmpadas, ações/clima)
  quebravam em várias linhas sem centralização, comendo a área do mapa.
- **Alertas no canto superior direito.**

## Correções (`frontend/index.html`, só em `@media (max-width:768px)`)
- **Mapa em tela cheia:** `.map-wrap { left:0; right:0; padding:0 }` e
  `#map { border-radius:0; border:none; box-shadow:none }`.
- **Header compacto e centralizado:** `.header-row` com `flex-wrap` + `justify-center`;
  título centralizado (subtítulo oculto no mobile); chips de clima + DB/GR/N
  centralizados; lâmpadas SAAM centralizadas; chips e ícones reduzidos para caberem.
- **Alertas centralizados** no topo (`.alert-toasts` left/right 8px, itens
  centralizados, largura máx. 420px).
- **Leaflet:** `syncHeaderHeightVar()` agora chama `map.invalidateSize()` após
  mudar a altura do header, evitando tiles deslocados/cinza ao recalcular o layout.

## Validações
- `node --check` no script do index.html → OK.
- Mockup do resultado: `docs/mockup_mobile_corrigido.png`.

## Arquivos alterados
- `frontend/index.html` — overrides mobile (mapa full-bleed, header centralizado,
  alertas centralizados) + `invalidateSize`.

## Ajustes adicionais (2ª rodada)
- **DB + GR + N agrupados e centralizados:** os três botões foram envolvidos em
  `.header-iconbtns`; no mobile, clima e botões ficam cada um em sua linha
  centralizada (antes o DB ficava solto na linha dos chips).
- **Conversa "limpa":** ao **encerrar a voz** a faixa de conversa é **limpa e
  ocultada** (`mConvoClear`); botão **×** para limpar manualmente; texto limitado a
  3 linhas (clamp). Enquanto a conversa está aberta, o **contador BG é ocultado**
  (`body.convo-open`) para não sobrepor o texto.
