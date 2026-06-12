# KRATOS — Mapa de Conhecimento (acessos de informação)

Autor: Jossian Brito

Inventário do que o KRATOS enxerga ao conversar (texto e voz). Fonte:
`_strategy_context_dict()` e `_kratos_voice_instructions()` em `main.py`.

## Acessos ativos

| # | Categoria | Campo no contexto | Conteúdo |
|---|-----------|-------------------|----------|
| 1 | Rebocadores SAAM | `saamTugs` | MMSI, nome, lat/long, velocidade (SOG), rumo, geofences em que está |
| 2 | Concorrentes (WIL/CAM) | `competitors` | nome, empresa, lat/long, se está em geofence de manobra e qual |
| 3 | **Todas as embarcações** | `vesselsOverview` | até 150 embarcações com posição: nome, MMSI, categoria, lat/long, SOG, parado/movendo, geofences, frota (SAAM/WIL/CAM quando aplicável) |
| 4 | **Geofences (demarcação)** | `geofencesMap` | nome, tipo, escopo, **vértices**, **centro (lat/long)**, dimensão aproximada (nm) ou raio (m) |
| 5 | **Distâncias / ETA** | `maneuverDistances` | para cada navio das próximas manobras: posição + distância (nm) e ETA (min, na velocidade atual) de cada rebocador nosso e concorrente |
| 6 | **Rastro / tendência** | `recentTracks` | deslocamento recente dos rebocadores: direção cardeal, distância percorrida, janela de tempo |
| 7 | Programação (Praticagem) | `scheduledManeuvers` | POB, navio, EMP.RB, LOA/boca/DWT, rebocadores estimados, valor comercial relativo, nossa/concorrente |
| 8 | Simultaneidade | `simultaneousManeuvers` | janelas com 2+ manobras e demanda estimada de rebocadores |
| 9 | Mudanças de programação | `scheduleChanges` | atrasos, adiantamentos, entradas/saídas |
| 10 | Meteocean | `metocean` | vento (velocidade/direção), maré (nível, tendência, próxima preia/baixa-mar) |
| 11 | Market share | `marketShare` | participação por EMP.RB (SAA = SAAM destacada) |
| 12 | Memória de aprendizado | `userLearnedNotes` | notas/regras registradas pelo usuário e interações passadas |
| 13 | **Perfil do usuário** | `userProfile` | nome, função e padrões de decisão (persistido em `kratos_user_profile.json`) |
| 14 | **Visão do mapa** | `userMapView` | centro, zoom e área visível (enviado pela voz ao vivo do mapa; aceito também no chat) |
| 15 | Histórico da conversa | `history` | últimos 8 turnos (texto); na voz, a própria sessão Realtime mantém o fio |

## Comportamentos ligados ao conhecimento

- **Primeiro contato**: sem perfil salvo, o KRATOS se apresenta e pergunta nome e
  função; quando o usuário informa, ele registra via tag interna `[PERFIL: ...]`
  (removida da resposta) e passa a chamar pelo nome.
- **Padrões de decisão**: preferências operacionais relatadas viram entradas em
  `patterns` no perfil (máx. 20) e são consideradas nas recomendações.
- **Foco**: a conversa é restrita a operações portuárias, navegação, apoio
  marítimo, meteorologia operacional, segurança da navegação e normas
  (NORMAM/Marinha do Brasil, SOLAS, MARPOL, COLREG). Fora disso, o KRATOS
  redireciona com cortesia. Em temas normativos críticos, recomenda confirmar
  na publicação oficial.

## Limitações conhecidas / próximas expansões

- **Reconhecimento de locutor (voz)**: a Realtime API da xAI não oferece
  identificação de quem fala; o perfil é por instalação (`DASHBOARD_USER_ID`).
  Possível evolução: perfis múltiplos com seleção manual.
- **Captura de perfil pela voz**: as tags `[PERFIL]` são processadas no chat de
  texto; na voz ao vivo o perfil é lido, mas novos dados informados por voz
  ainda não são persistidos automaticamente.
- **Trilhas longas**: `recentTracks` usa o buffer recente (~4000 posições);
  histórico de horas/dias exigiria persistência dedicada.
- **Áreas de interesse**: lista a ser definida com o usuário (normas
  específicas, terminais, classes de navio etc.).
