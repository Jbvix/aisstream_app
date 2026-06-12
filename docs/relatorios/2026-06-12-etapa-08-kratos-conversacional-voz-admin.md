# Relatório de Etapa 08 — KRATOS Conversacional, Voz ao Vivo e Administração

Autor: Jossian Brito

- **Data:** 2026-06-11 a 2026-06-12
- **Branch de trabalho:** `claude/lucid-sagan-wtrko`
- **Intervalo:** `227cecd` → `1b1042f` (12 commits)

Etapa que elevou o KRATOS de um assistente de pergunta-e-resposta a um
**interlocutor estratégico conversacional com voz ao vivo**, expandiu o seu
conhecimento operacional, deu gestão dinâmica de frota e criou a página do
administrador para comprovar eficácia.

---

## 1. Implementações (features novas)

| Área | Entrega | Commit |
|------|---------|--------|
| Assistente | Campo conversacional com memória de turno (até 8 trocas) + persona estrategista | `227cecd` |
| Voz | Voz do navegador: KRATOS fala (TTS) e escuta (STT) — Web Speech API | `db00d74` |
| Voz | **Voz ao vivo** com xAI Realtime Voice API (voz Leo), token efêmero do backend | `da0a8a9` |
| Voz | Voz ao vivo também no mapa + módulo compartilhado `kratos-voice.js` (lazy) | `7a26f95` |
| Conhecimento | Embarcações (todas), demarcação de geofences, distâncias/ETA, rastros, visão do mapa e perfil do usuário | `d1bf96f` |
| Frota | Gestão dinâmica de MMSIs (painel Frota no mapa) + verificação "barra fora" pelo KRATOS | `a71c25b` |
| UX/Guia | Guia da interface + tour guiado por partes | `5f0d91b` |
| Geofence | Tipo "corredor de tráfego" (rota navegável nomeada) | `14a1699` |
| Admin | Página do administrador (`/admin`): eficácia, uso e auditoria, protegida por `ADMIN_TOKEN` | `1b1042f` |

## 2. Melhorias

- **Conversa comedida e reativa**: responde só o que é perguntado, em partes
  curtas; à saudação, cumprimenta, pergunta o nome e fica à disposição (`960611e`).
- **Ícones** em seta esguia (estilo MarineTraffic) e diagnóstico de erro de voz
  acionável (fim do "erro: desconhecido") (`7a26f95`).
- **Botão "Isso foi útil? 👍/👎"** na última resposta do KRATOS (telemetria de valor).

## 3. Correções

- **Linguagem**: o "enxadrista" virou só mentalidade interna; o KRATOS fala a
  terminologia de navegação/apoio portuário, sem termos de xadrez (`b05cda1`).
- **Unidades/siglas por extenso** na fala: "milhas náuticas" (nm), "nós" (kn),
  "SAAM" como palavra, POB/MMSI/AIS soletrados (`14dd507`).
- **Distância ciente dos corredores**: a linha reta passou a ser tratada como
  referência mínima; o trajeto real segue o corredor navegável (`14dd507`).
- **Bug do SOG**: a velocidade dos rebocadores no contexto lia campo inexistente
  (`speed`); passou a usar o SOG real do AIS (corrige ETA) (`d1bf96f`).

## 4. Reconciliação Git

No início da etapa, o `main` do servidor havia divergido (trabalho paralelo de
Obsidian/Grafo). Resolvido por rebase preservando ambos os conjuntos; o servidor
foi realinhado ao GitHub com backup (`backup-prod-pre-obsidian`).

## 5. Decisões de produto / comercial

- **Monetização**: não cobrar agora; usar 2–3 meses como piloto instrumentado e
  cobrar quando houver hábito diário + um número que prove valor. Modelo:
  assinatura por operação/porto, 3 planos, **exclusividade por porto** como
  premium, preço ancorado no valor de uma manobra. Formalizar a relação com a SAAM.
- A **página do administrador** é a instrumentação desse "Número".

## 6. Arquitetura / persistência (runtime, gitignored)

- `kratos_user_profile.json` — perfil do usuário (nome, função, padrões).
- `fleet_config.json` — frota SAAM/WIL/CAM editável.
- `kratos_events.jsonl` — telemetria de uso/auditoria (rolling ~5000).

## 7. Lições aprendidas

- **O xAI evoluiu durante a etapa.** A Realtime Voice API (voz Leo) não existia
  quando começamos; ao surgir, migramos do TTS do navegador para a voz nativa do
  Grok. Lição: revalidar premissas de API antes de fechar arquitetura.
- **Cérebro x voz são camadas distintas.** Grok pensa (texto), Realtime fala —
  separar deixou claro o que configurar (`XAI_API_KEY` + endpoint Voice).
- **Token com `#` quebra env var no cPanel.** Use `.env` (já carregado por
  `load_dotenv`) e evite `#` em segredos.
- **Casar por tipo, não por nome** (corredores/base): nomes variam, tipo é estável.
- **Comedimento é feature.** Um assistente que despeja dados afasta; responder só
  o perguntado, em partes, foi pedido explícito do usuário e melhora a adoção.
- **Reusar módulo (voz) entre páginas** via arquivo compartilhado lazy evitou
  ~200 linhas duplicadas e manteve painel e mapa consistentes.

## 8. Pendências / próximos passos

- Cálculo numérico de distância **projetada no corredor** (hoje é descritivo).
- Persistir perfil informado **por voz** (hoje só via chat de texto).
- Múltiplos perfis de usuário (a Realtime API não identifica locutor).
- Definir a **lista de áreas de interesse** e normas (NORMAM/SOLAS/MARPOL/COLREG)
  prioritárias.
- Contador explícito de "manobras antecipadas pelo KRATOS" para reforçar o Número.
