# Etapa 10 — Normas locais (NPCP-RJ) como conhecimento estratégico do KRATOS

Autor: Jossian Brito

Data: 2026-06-12

## Objetivo

Analisar, estruturar e incorporar ao conhecimento do KRATOS as duas portarias da
Capitania dos Portos do Rio de Janeiro que alteram a NPCP-RJ (3ª Revisão),
tratando-as como **informação estratégica** (foco em demanda de rebocador,
janelas de manobra e restrições operacionais).

## Fontes analisadas
- Portaria CPRJ/COMOPNAV/MB nº 11, de 06/03/2026 (caps. 4 e 5 da NPCP-RJ).
- Portaria nº 110/CPRJ/COMOPNAV/MB, de 14/05/2026 (cap. 5 — EISA e Angra/TPAR).

## O que foi implementado

### Backend (`main.py`)
- Nova constante `KRATOS_NPCP_KNOWLEDGE` (~4,8 mil caracteres): destilado
  estratégico das duas portarias, organizado por **demanda de rebocador por área**
  (ferro-gusa: 1×≥45 TTE + 1×≥25 TTE; Angra/TPAR: ≥2 azimutais ≥45 TTE; EISA:
  reboque obrigatório), **onde o DP dispensa reboque** (Brasco-Niterói; EAM DP em
  Angra), **navios-tipo**, **canais/calados/restrições de porte** (Cais Comercial,
  TECON-RJ até 349 m LOA, restrição diurno-only 150–185 m no trecho 197–216) e
  **praticagem ZP-15** (ERU 58/quadrimestre, cotas por subzona, período de escala).
- Injetada nos **dois** caminhos de conversa: chat de texto (`_ask_grok_with_context`)
  e voz ao vivo (`_kratos_voice_instructions`) — o KRATOS responde por texto e voz
  com base nas normas, citando portaria/terminal e recomendando confirmar a fonte
  oficial em decisão crítica.

### Documentação
- `docs/conhecimento/npcp-rj-portarias-2026.md`: referência humana estruturada
  (tabelas de demanda por área, calados por trecho, praticagem) e rotina de
  manutenção.
- `docs/KRATOS_CONHECIMENTO.md`: nova linha (#18) no mapa de acessos do KRATOS.
- `frontend/dashboard.html`: Manual do usuário — novo item explicando que o KRATOS
  conhece as normas locais e exemplos de pergunta.

## Enquadramento estratégico (resumo)
- **Mais demanda da nossa frota:** ferro-gusa (recorrente, 2 rebocadores), Angra/TPAR
  (azimutais pesados), EISA (reboque obrigatório de cascos).
- **Menos demanda:** terminais onde o DP dispensa reboque (Brasco-Niterói; EAM DP).
- **Concentração temporal:** restrição diurno-only para navios grandes no TECON
  concentra manobras de dia — antecipar pico e sobreposição.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- Conferência: bloco presente e 2 injeções (texto + voz).

## Manutenção futura
Novas portarias/alterações da NPCP-RJ: atualizar a constante `KRATOS_NPCP_KNOWLEDGE`
e o doc `docs/conhecimento/npcp-rj-portarias-2026.md`, mantendo as datas de vigência.

## Arquivos alterados
- `main.py` — `KRATOS_NPCP_KNOWLEDGE` + injeção no chat e na voz.
- `docs/conhecimento/npcp-rj-portarias-2026.md` — referência estruturada (novo).
- `docs/KRATOS_CONHECIMENTO.md` — linha #18 no mapa de conhecimento.
- `frontend/dashboard.html` — Manual do usuário.
