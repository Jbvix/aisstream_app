# Runbook de Operacao em Producao

## Objetivo
Padronizar diagnostico e resposta para incidentes operacionais do `aisstream_app`.

## 1) Falha de WebSocket em producao

### Sintoma
- Frontend exibe erro de conexao `wss://.../ws failed`.
- Console mostra tentativas repetidas de reconexao.

### Diagnostico
1. Verificar se host esta em ambiente com proxy/restricao de upgrade WS.
2. Validar status backend via `/api/status`.
3. Confirmar que fallback para polling esta ativo quando necessario.

### Acao
- Manter frontend em modo polling para hosts com restricao de WebSocket.
- Validar fluxo de atualizacao de alvos no mapa.

### Validacao final
- Sem spam de erro de WS no console.
- Alvos atualizando via polling.

---

## 2) Deploy bloqueado no cPanel (working tree suja)

### Sintoma
- Deploy HEAD Commit falha com mensagem de impossibilidade de deploy.

### Diagnostico
1. Executar `git status --porcelain` no servidor.
2. Verificar arquivos runtime em `data/users/default/`.

### Acao
- Seguir procedimento em `DEPLOY_CPANEL.md`.

### Validacao final
- `git status` limpo.
- Deploy executado com sucesso.

---

## 3) Queda de dados AIS em tempo real

### Sintoma
- `liveConnected=false` e `totalMessages=0`.

### Diagnostico
1. Verificar chave AISSTREAM ativa e sem duplicidade em outro app.
2. Confirmar conectividade externa e limites de conta.
3. Revisar logs do backend.

### Acao
- Corrigir configuracao de credenciais/chaves.
- Reiniciar servico se necessario.

### Validacao final
- `liveConnected=true`.
- `lastAisMessageAt` atualizando.

