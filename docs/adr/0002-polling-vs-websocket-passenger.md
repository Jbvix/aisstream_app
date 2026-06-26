# ADR 0002 - Transporte de dados AIS: polling em produção (WebSocket não disponível)

## Status
Aceito

## Contexto
O app nasceu com WebSocket (`/ws`) para empurrar AIS ao vivo. Em produção roda sob
Passenger + a2wsgi (WSGI). **WSGI não suporta WebSocket** — o handshake retorna 200
em vez de 101. Confirmado em produção (origin 200, sem upgrade).

## Opções consideradas
- A) Manter só WebSocket.
- B) Polling HTTP periódico (`/api/vessels?since=`).
- C) Migrar hospedagem para ASGI puro (uvicorn/gunicorn-uvicorn).

## Decisão
B em produção: `tuglife.live` está em `FORCE_POLLING_HOSTS` (poll ~0,8 s,
incremental por `since`). WebSocket é mantido no código para ambientes ASGI
(desenvolvimento/futuro). C fica como evolução.

## Consequências
- (+) Funciona no cPanel atual sem trocar de host.
- (+) Snapshot persistido → mapa abre povoado mesmo após restart.
- (−) Latência de até ~1 s e mais requisições. Aceitável para a operação.
- (−) Dados ficam atrás do gate de acesso (polling 401 quando sessão inválida) →
  tratado com redirect ao login. Ver ADR 0004.

## Referências
`main.py` (relay/worker, `/api/vessels`), `frontend/index.html`
(`FORCE_POLLING_HOSTS`, `pollOnce`), `docs/relatorios/2026-06-15-fix-alvos-401-sessao.md`.
