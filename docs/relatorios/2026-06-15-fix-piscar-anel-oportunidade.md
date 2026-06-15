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
