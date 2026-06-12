# Etapa 11 — NPCP-RJ completa (3ª Revisão) no conhecimento do KRATOS

Autor: Jossian Brito

Data: 2026-06-12

## Objetivo

Incorporar ao KRATOS a **NPCP-RJ (3ª Revisão, Mod.2) completa** (344 slides, 6
capítulos) como informação estratégica, complementando as duas portarias já
adicionadas na Etapa 10. Foco: a **escada de reboque por porte (TTE)**, que é a
métrica direta de demanda da frota SAAM.

## Fonte
- `NPCPRJ__3Rev1__Mod2.pptx` — Normas e Procedimentos da Capitania dos Portos do
  Rio de Janeiro (3ª Revisão), texto OSTENSIVO. Extraído (texto + tabelas) e
  preservado em `docs/conhecimento/fontes/npcp-rj-3rev-mod2-extraido.md` (~502 mil
  caracteres).

## O que foi implementado

### Backend (`main.py`)
- `KRATOS_NPCP_KNOWLEDGE` expandida (~8,3 mil caracteres) com:
  - escopo da norma (6 capítulos) e da jurisdição **ZP-15** (Guanabara, Sepetiba/
    Itaguaí, Ilha Grande/Angra, Açu, Paraty, Forno);
  - **escada de reboque por porte** (LOA/boca/calado → nº de rebocadores e TTE),
    da regra geral do Porto do Rio aos navios de 295–349 m no TECON-RJ;
  - terminais de alta demanda (gás/LNGC = 5 rebocadores; píeres de petróleo ≥ 50
    TTE; quadro de boias; carga perigosa por DWT);
  - regras de ouro (rebocador/bow thruster obrigatório não dispensável; praticagem
    obrigatória ≥ 500 AB; PEP);
  - fundeadouros numerados, velocidade em canais e canais VHF (12/16);
  - instrução de uso: cruzar porte do navio + terminal com a escada para estimar a
    demanda da SAAM, citando a faixa e recomendando a fonte oficial.
- Continua injetada nos **dois** caminhos: chat de texto e voz ao vivo.

### Documentação
- `docs/conhecimento/npcp-rj-3rev-resumo-estrategico.md` — resumo estratégico da
  norma completa (tabela da escada de reboque, terminais, fundeadouros,
  implicações táticas).
- `docs/conhecimento/fontes/npcp-rj-3rev-mod2-extraido.md` — texto integral
  extraído (fonte de referência e busca).
- `docs/KRATOS_CONHECIMENTO.md` — linha #18 atualizada para a norma completa.

## Escopo e limitações
- A extração do PPTX é fragmentada; a escada de reboque e os parâmetros-chave foram
  consolidados de forma confiável, mas **nem todo terminal individual** foi mapeado
  linha a linha no prompt. O texto integral fica na pasta `fontes/` para refinamento
  incremental. Em decisão crítica, o KRATOS recomenda confirmar na NPCP-RJ oficial.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- Bloco `KRATOS_NPCP_KNOWLEDGE` ~8,3k chars, 2 injeções (texto + voz).

## Arquivos alterados
- `main.py` — expansão de `KRATOS_NPCP_KNOWLEDGE`.
- `docs/conhecimento/npcp-rj-3rev-resumo-estrategico.md` (novo).
- `docs/conhecimento/fontes/npcp-rj-3rev-mod2-extraido.md` (novo, fonte integral).
- `docs/KRATOS_CONHECIMENTO.md` — linha #18.
