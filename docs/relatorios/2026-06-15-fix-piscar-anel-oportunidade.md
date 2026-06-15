# Correção — alvos "piscando" (anel de oportunidade)

Autor: Jossian Brito

Data: 2026-06-15

## Sintoma
Após as Etapas 14/16 entrarem em produção (visíveis agora que a sessão foi
restabelecida), os alvos voltaram a "piscar".

## Causa
O **anel âmbar de oportunidade** (Etapa 16) era **pulsante** (animação
`opportunityPulse`). Pior: a marcação "sem contrato" usava
`!programmedNames.has(nome)` mesmo quando `programmedNames` estava **vazio**
(programação da Praticagem ainda não carregada/sincronizada). Resultado: **todos**
os navios mercantes ≥ 120 m dentro da BG ganhavam o anel pulsante ao mesmo tempo —
dezenas de anéis pulsando = sensação de "piscar".

(O caminho de marcador em si está estável: a assinatura de ícone não recria por
tick para alvos parados; o efeito era a animação do anel em massa.)

## Correção (`frontend/index.html`)
1. **Guarda de dados:** só marca "sem contrato" quando há programação para
   comparar — `programmedNames.size > 0`. Sem a programação, nenhum alvo é
   classificado como oportunidade (evita falso-positivo em massa).
2. **Anel fixo:** removida a animação de pulso; o anel de oportunidade agora é
   **âmbar estático** (continua distinto do vermelho de concorrente e o alvo
   também aparece na lista "Oportunidades agora").

## Validações
- `node --check` no script do `index.html` → OK.
- Sem referências órfãs a `opportunityPulse`.

## Arquivos alterados
- `frontend/index.html` — guarda `programmedNames.size > 0`; anel de oportunidade
  sem animação.

## Segunda rodada — recriação de ícone por ruído de heading (parados)

Persistindo o "piscar", a causa principal era a **assinatura do ícone**
(`vesselIconSignature`) incluir o `rotStep` (rumo) **mesmo para alvos parados**.
Parado em zoom normal é renderizado como **círculo** (rotação irrelevante), mas o
heading "treme" alguns graus a cada report AIS → a assinatura mudava a cada tick →
`setIcon` recriava o DOM do marcador (pisca), sem mudança visual. Com a frota
majoritariamente atracada, isso fazia "todos piscarem".

Correção: o `rotStep` só entra na assinatura quando há **seta** (em movimento) ou
**casco em escala real** (zoom ≥ 14); parado em zoom normal usa `rotStep = 0`
(estável). Passos de **6°** (antes 3°) reduzem a recriação de quem está em
movimento. Resultado: alvos parados não recriam ícone por ruído de rumo.
