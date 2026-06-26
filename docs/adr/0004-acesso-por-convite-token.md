# ADR 0004 - Controle de acesso por convite (token), não login/senha

## Status
Aceito

## Contexto
O app (mapa + painel) era aberto a quem tivesse a URL. Necessário restringir a
convidados, sem montar cadastro/senha/SMTP, e sem risco de trancar o dono.

## Opções consideradas
- A) Login usuário/senha + banco.
- B) Token de convite por link (WhatsApp/e-mail), cookie de sessão.
- C) Sem controle.

## Decisão
B. Convites com `secrets.token_urlsafe` (rótulo, validade, revogação) em
`data/users/<id>/access_invites.json`. Middleware exige token (cookie `kratos_access`,
`?access=` ou header) quando `ACCESS_CONTROL=on`. Exceções: `/entrar`, `/api/access/*`,
`/admin`, `/api/admin/*`, estáticos. `ADMIN_TOKEN` = chave-mestra. **Kill-switch:**
`ACCESS_CONTROL` desligado por padrão (deploy não tranca o site).

## Consequências
- (+) Simples, sem senhas/SMTP; convites por link prontos (wa.me/mailto).
- (+) Sem lockout (chave-mestra) e ativação controlada por env.
- (−) Tokens são segredos → arquivo gitignored.
- (−) WebSocket não é coberto pela trava HTTP (só páginas/REST). Em produção é
  polling, então os dados ficam protegidos na prática.

## Referências
`main.py` (núcleo de convites + middleware), `frontend/entrar.html`,
`frontend/admin.html` (aba Convites), `docs/PAGINA_ADMIN.md`.
