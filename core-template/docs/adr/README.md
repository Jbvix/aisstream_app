# ADR — Architecture Decision Records

Autor: Jossian Brito

Este diretório guarda os registros de decisões arquiteturais do projeto.

## Quando criar um ADR
- Ao escolher entre abordagens com trade-offs relevantes.
- Ao alterar comportamento de integração (ex.: WebSocket, polling, APIs externas).
- Ao definir padrões permanentes de arquitetura.

## Padrão de nome
- `0001-titulo-curto.md`, `0002-titulo-curto.md`, …

## Template

```md
# ADR 000X - Título da decisão

Autor: Jossian Brito

## Status
Proposto | Aceito | Substituído | Obsoleto

## Contexto
Problema e motivação da decisão.

## Opções consideradas
- Opção A
- Opção B
- Opção C

## Decisão
Escolha final e justificativa.

## Consequências
Impactos positivos, riscos e limitações.

## Referências
Links para PRs, issues, docs e métricas.
```

## Herdados do KRATOS Core (já decididos)
- Acesso por convite (token) com kill-switch e chave-mestra.
- Suporte a subcaminho via `root_path`.
- Polling quando o host não suporta WebSocket (WSGI/Passenger).

Reescreva-os como ADRs do novo app apenas se o domínio mudar a decisão.
