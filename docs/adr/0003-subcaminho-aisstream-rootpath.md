# ADR 0003 - App montado sob subcaminho /aisstream (root_path)

## Status
Aceito

## Contexto
Em produção o app vive em `https://tuglife.live/aisstream/` (Passenger define
`SCRIPT_NAME=/aisstream`). `request.url.path` chega COM o prefixo, o que quebra
checagens de rota absolutas e redirects/links.

## Opções consideradas
- A) Assumir app na raiz `/` (quebra em produção).
- B) Tratar o `root_path`/prefixo explicitamente onde o caminho importa.

## Decisão
B. No backend, `_app_relative_path()` remove o `root_path` antes de comparar rotas
(ex.: isenções do gate) e os redirects preservam o prefixo (`{root}/entrar`). No
frontend, `BASE_PATH`/`apiUrl()` e links (splash → `/versao`) montam URLs relativas
ao subcaminho.

## Consequências
- (+) Funciona igual na raiz (dev) e sob `/aisstream` (produção).
- (−) Exige lembrar do prefixo em todo redirect/link/cookie novo.
- Cookies usam `Path=/` (cobre o subcaminho).

## Referências
`main.py` (`_app_relative_path`, `access_gate_middleware`),
`docs/relatorios/2026-06-12-etapa-13-acesso-por-convite.md` (correção Passenger).
