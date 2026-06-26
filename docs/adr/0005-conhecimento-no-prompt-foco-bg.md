# ADR 0005 - Conhecimento normativo (NPCP-RJ) embutido no prompt, foco BG

## Status
Aceito

## Contexto
O assistente (Grok) precisa raciocinar com as normas locais (calados, janelas,
exigência de rebocadores/TTE por terminal). Documento oficial é extenso (toda a
ZP-15) e a operação foca a Baía de Guanabara.

## Opções consideradas
- A) RAG/embeddings com busca semântica.
- B) Constante destilada no prompt (`KRATOS_NPCP_KNOWLEDGE`), foco BG.
- C) Não embutir (assistente genérico).

## Decisão
B. Conhecimento destilado em constantes `KRATOS_*` injetadas no system prompt
(texto e voz). Foco BG (terminal a terminal); demais subzonas como contexto. Texto
integral preservado em `docs/conhecimento/fontes/` para refino. Upload de arquivo no
chat complementa (índice + trechos relevantes por palavra-chave — sem embeddings).

## Consequências
- (+) Respostas com base normativa, sem infra de RAG; rápido e barato.
- (+) Atualização simples (editar constante + doc).
- (−) Custo de tokens por requisição (prompt maior); mitigado pelo recorte BG.
- (−) Relevância por palavra-chave (não semântica) no upload — suficiente no volume atual.

## Referências
`main.py` (`KRATOS_NPCP_KNOWLEDGE`, `_build_user_knowledge_block`),
`docs/conhecimento/`, relatórios das etapas 10–12 e 18.
