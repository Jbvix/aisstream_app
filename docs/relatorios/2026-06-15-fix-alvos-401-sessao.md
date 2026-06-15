# Correção — alvos não aparecem (sessão de acesso / 401)

Autor: Jossian Brito

Data: 2026-06-15

## Sintoma
Mapa carrega, mas **sem alvos** em produção (tuglife.live).

## Diagnóstico
- **AIS está vivo:** os logs do servidor registram evento de embarcação
  (`[EVENT] EXIT | MMSI:710510000 | NSS GUILLOBEL | -22.97,-43.13`) — o backend
  recebe e processa AIS normalmente.
- **Produção não usa WebSocket:** `wss://tuglife.live/aisstream/ws` responde
  **HTTP 200** (não faz upgrade 101) — Passenger/a2wsgi (WSGI) não suporta
  WebSocket. Por isso `tuglife.live` está em `FORCE_POLLING_HOSTS` e o mapa
  sempre se alimenta por **polling** `/api/vessels`.
- **ACCESS_CONTROL=on** passou a **gated** os endpoints de dados:
  `/api/vessels` e `/api/status` retornam **401** sem sessão válida. Confirmado:
  401 sem cookie; **200 com cookie/`?access=`/master**.
- O `pollOnce` **engolia o 401 em silêncio** → o mapa abria (HTML do cache) e
  ficava sem alvos, sem explicação.

## Causa raiz
Navegador/dispositivo **sem cookie de acesso válido** (HTML servido do cache
enquanto a sessão não existia/expirou) + endpoints de dados protegidos →
polling 401 → nenhum alvo, silenciosamente.

## Correção (frontend)
- `handleAuthRequired(res)`: ao receber **401** no polling/hidratação
  (`pollOnce`, `hydrateVesselsFromApi`), **redireciona para `/entrar`** (login),
  que regrava o cookie de convite — em vez de exibir o mapa vazio.

## Ação do usuário
- Reentrar pelo **link de convite** (ou `…/aisstream/?access=<ADMIN_TOKEN>` como
  chave-mestra) para regravar a sessão. Com sessão válida, o polling volta a
  200 e os alvos aparecem.

## Observação estrutural
- Em produção (Passenger/WSGI) **não há WebSocket**; o dado vem por polling.
  Migrar para um host ASGI (uvicorn/gunicorn-uvicorn) habilitaria WS — fora do
  escopo desta correção.

## Arquivos alterados
- `frontend/index.html` — `handleAuthRequired` + tratamento de 401 no polling.
