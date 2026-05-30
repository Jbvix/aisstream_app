# Assistente de Estrategias (Grok) - Instrucoes Operacionais

## Objetivo

Entregar apoio decisorio para operacao portuaria, com foco em:
- Posicao atual dos rebocadores SAAM.
- Programacao de manobras (Praticagem-RJ).
- Presenca de concorrentes em geofence de manobra.
- Avaliacao meteoceanica (vento e maré).
- Identificacao de manobras simultaneas.
- Estimativa de rebocadores necessarios por navio.
- Geração de relatorios e insights executivos.

## Fontes de contexto usadas pelo assistente

- Frota SAAM em tempo real (buffer AIS).
- Tabela sincronizada de manobras (`saa_maneuvers.json`).
- Geofences ativas (`berco` e `polygon` para status de manobra).
- Lista de concorrentes (WIL e CAM por MMSI).
- Market share por `EMP.RB`:
  - consolidado;
  - janelas `hoje`, `7 dias`, `30 dias`.
- Condicoes ambientais:
  - vento atual (integracao online);
  - maré (placeholder operacional ate conectar fonte hidrografica oficial).
- Memoria de aprendizado do usuario (`strategy_memory.json`).

## Como usar no Dashboard

1. Abra `Dashboard`.
2. Na secao **Assistente de estrategias (Grok)**:
   - escreva a pergunta na caixa principal;
   - opcionalmente adicione uma regra em **Aprendizado**;
   - escolha acao:
     - **Consultar assistente**: resposta direta;
     - **Gerar relatorio**: texto executivo consolidado;
     - **Gerar insights**: hipoteses e oportunidades acionaveis.

## Padrao de resposta esperado

O assistente deve responder em portugues, de forma objetiva, cobrindo quando relevante:
- cenario atual de operacao;
- risco operacional (vento/maré);
- concorrencia em manobra;
- simultaneidade e demanda estimada de rebocadores;
- recomendacoes praticas de alocacao.

## Regras de estimativa (versao inicial)

Estimativa de rebocadores por navio (heuristica inicial):
- LOA >= 300m ou DWT >= 100000: **4 rebocadores**;
- LOA >= 230m ou DWT >= 60000: **3 rebocadores**;
- demais casos: **2 rebocadores**.

> Observacao: regra demonstrativa. Ajustar com historico operacional local e validacao da equipe.

## Aprendizado com o usuario

- O campo de aprendizado registra orientacoes operacionais em memoria local.
- Cada interacao pode adicionar conhecimento para contexto futuro.
- Recomenda-se registrar regras curtas e acionaveis, por exemplo:
  - "Navio com boca acima de 45m exige abordagem conservadora."
  - "Com vento lateral forte no canal, antecipar reforco de 1 rebocador."

## Relatorios e insights

Os relatorios devem priorizar:
- resumo executivo em bullets;
- situacao por janela temporal de market share;
- riscos de janelas com manobras simultaneas;
- plano de acao (curto prazo).

## Proximos incrementos recomendados

- Integrar fonte oficial de maré para Rio de Janeiro.
- Ajustar modelo de estimativa de rebocadores com historico real (feedback loop).
- Adicionar score de confianca por recomendacao.
- Exportar relatorio em PDF/CSV.
