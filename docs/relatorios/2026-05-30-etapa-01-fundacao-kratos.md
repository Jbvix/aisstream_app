# Relatório de Etapa 01 — Fundação do KRATOS

- **Data:** 2026-05-30
- **Branch de trabalho:** `claude/lucid-sagan-wtrko`
- **Baseline:** `715c854` → **Entrega:** `38b09c9`
- **Commits na etapa:** 18

Etapa de consolidação: estabelecer o pipeline de deploy, dar identidade ao
produto (KRATOS) e elevar a inteligência estratégica visível no mapa e no painel.

---

## 1. Implementações (features novas)

| Área | Entrega | Commit |
|------|---------|--------|
| Documentação | Proposta KRATOS + guia de pull/deploy cPanel (estrutura flat) | `cc76349` |
| Mapa | Redesenho dos ícones de embarcações (casco SVG, estado, concorrentes) | `a7e7954` |
| Mapa | Ícones no padrão AIS (seta direcional, parado = círculo) | `be21582` |
| Mapa | Tamanho por classe de comprimento + escala no zoom (modelo MarineTraffic) | `070b6b0` |
| Marca | Renomeação completa do app para **KRATOS** (mapa, painel, backend) | `d49e03d`, `6acc4be` |
| Painel | Reposicionamento de KRATOS/Monitor ao topo + splash screen + manual | `62ef736` |
| Mapa | Persistência das embarcações após refresh (backend em disco + cache no F5) | `22fa833` |
| Mapa | Destaque dos nomes dos navios que a SAAM vai manobrar (label dourado) | `6b2e2ec` |
| Mapa | Caixa de insights do KRATOS (datilografada, ao vivo) por regras | `ef80452` |
| Meteocean | Maré real via Open-Meteo Marine nos insights | `c5ab3a4` |
| Insight | KRATOS informa rebocadores SAAM na base de rebocador (BASE BRASCO) | `38b09c9` |

## 2. Melhorias

- **SAA = SAAM** tratado explicitamente no market share e no prompt do KRATOS;
  fatia da SAAM destacada no gráfico (`9d66d1b`, `8ac5571`).
- **Maré do header** migrada de altura de onda para nível do mar real,
  consistente com os insights (`de92a15`).
- **Manual do usuário** sincronizado com cada feature visível, com rodapé de
  "última atualização" (`a3f3702` e seguintes).

## 3. Correções

- Frota SAAM: **SAAM ARIES → SAAM PATAXO** (`710012550`) — `9ea339e`.
- Frota SAAM: **SAAM ITABIRA → SAAM PARECI** (`710001249`) — `6c9cf4d`.
- Insight/market share: remover "(nós)", exibir apenas **SAAM** — `8ac5571`.
- Reconciliação Git: GitHub passou a ser a fonte da verdade (flat), com o
  histórico real do cPanel publicado e o clone reapontado ao GitHub.

## 4. Infra / Deploy

- Pipeline **GitHub → cPanel** configurado (origin do clone aponta ao GitHub).
- `.gitignore` ajustado para não versionar runtime: snapshot de embarcações,
  e `pitch/` (material fora do projeto).
- Convenção de trabalho registrada em `CLAUDE.md` (atualizar manual a cada
  implementação; validar sintaxe; fast-forward de `main`).

## 5. Lições aprendidas

- **Casar por identidade estável, não por rótulo.** A geofence da base aparecia
  como "BASE BRASCO" num ambiente e "base rebocador" noutro; a solução robusta
  foi casar pelo **tipo** `base_rebocador` e exibir o nome real dinamicamente.
- **Persistência muda a percepção.** Sem snapshot em disco, todo deploy/restart
  do Passenger abria o mapa vazio; persistir resolveu o "sumiço após refresh".
- **Insights por regras antes de IA.** Gerar insights determinísticos (rápidos,
  grátis, sempre disponíveis) deu valor imediato sem custo de chamada ao Grok;
  a camada de IA pode enriquecer depois, com throttle.
- **Fonte única para cada dado.** Maré no header e nos insights divergiam;
  unificar a fonte (Open-Meteo Marine) eliminou inconsistência.
- **Validar antes de commitar evita ruído.** `node --check` e `ast.parse`
  pegaram erros cedo; cuidado extra: `import main` em smoke-test reescreve
  `geofences.json` (efeito colateral) — restaurar antes de commitar.
- **Documentar a divergência Git cedo.** O cPanel tinha histórico que o GitHub
  não tinha; mapear isso antes evitou um merge de árvores não relacionadas.

## 6. Pendências / próximos passos

- Camada opcional de IA (Grok) intercalando 1–2 insights narrativos, com throttle.
- Estado "envelhecido" (esmaecido) para embarcações restauradas do snapshot até
  a 1ª atualização AIS.
- Previsão de janelas de manobra e detector de oportunidades (Fase 3 do roadmap).
- Confirmar saída de rede do cPanel para `marine-api.open-meteo.com`.
