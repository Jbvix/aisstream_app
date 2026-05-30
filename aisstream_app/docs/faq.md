# FAQ e Troubleshooting

## 1) Por que o mapa mostra erro de WebSocket em producao?
Em alguns hosts, o proxy/origem nao permite upgrade WS corretamente. Nesses casos, o sistema deve operar em polling para manter estabilidade.

## 2) O deploy no cPanel esta bloqueado. O que fazer?
Consulte `DEPLOY_CPANEL.md` e limpe a working tree no servidor antes de executar o deploy.

## 3) Os alvos AIS param de aparecer. O que validar primeiro?
- Endpoint `/api/status`
- Chave AISSTREAM ativa e unica
- Logs de conexao do backend

## 4) Geofence principal da Baia de Guanabara pode ser removida?
Nao. Ela e persistente por regra de negocio para monitoramento BG/MAR.

## 5) O que fazer quando houver regressao visual no mapa?
Registrar no changelog, abrir ADR se houver mudanca arquitetural e atualizar runbook/FAQ com o novo comportamento.

