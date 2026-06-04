# Relatório de Etapa 06 — Integração Obsidian (Homologação e correções de deploy)

- **Data:** 2026-06-04
- **Branch de trabalho:** `claude/nifty-ride-Wj6RC`
- **Escopo:** colocar a integração Obsidian em produção (cPanel + Supabase) e
  corrigir o que apareceu na homologação real.

---

## 1. Diagnóstico em produção

| Sintoma | Causa raiz | Correção |
|---------|-----------|----------|
| `…/api/obsidian/status` → `Not Found` | servidor rodava código antigo; `main` local divergiu | `git merge origin/main --no-edit` (merge limpo, preservou 3 commits de produção) + restart |
| `export`/`test-upload` → `502` em ~0,4 s | `SUPABASE_KEY` recebeu uma **chave S3** (hex), não a **API key `service_role`** (JWT `eyJ…`) → Supabase: *"Invalid Compact JWS"* | usar a `service_role` de **Project Settings → API** |
| `export` → `502` em ~20 s | vault completo excede o **timeout do gateway** (Cloudflare ~20 s) | `/export` passa a rodar **em segundo plano** e responde na hora |

## 2. Implementações desta etapa

- **`/api/obsidian/export` não-bloqueante:** dispara `_run_obsidian_export_safe`
  via `asyncio.create_task` e retorna `{"status":"started"}` imediatamente.
  Mantém modo síncrono opcional para diagnóstico via `?wait=1`. Guarda de
  reentrância evita envios concorrentes.
- **Dashboard:** botão trata `started`/`running`, agenda refresh do status e a
  linha de estado passa a mostrar o **horário da última sincronização**
  (`lastExportTs`).
- **Manual do usuário** atualizado (envio em segundo plano + última sync).

## 3. Estado homologado

- `status` → `configured: true`, `autoSync: true` (5 min).
- `test-upload` → `ok:true` (nota de saúde gravada).
- Bucket `kratos-vault` populado: `kratos/` com `_sistema/`, `bercos/`, `dias/`,
  `empresas/`, `navios/`, `rebocadores/` e `KRATOS.md`.
- Auto-sync em segundo plano confirmado (uploads fora do gateway, sem 502).

## 4. Lições aprendidas

- **Cloudflare mascara o corpo de respostas 5xx** do origin: por isso o `502`
  aparecia como página genérica em vez do nosso JSON de erro. Diagnóstico exigiu
  reproduzir o upload direto no Supabase.
- **Dois "service_role" no Supabase:** a *API key* (JWT, para REST) e uma *S3
  access key* que o usuário pode nomear "service_role". São coisas distintas — o
  backend precisa do **JWT**.
- Operações longas atrás de um gateway com timeout curto devem ser
  **assíncronas/fire-and-forget**, não síncronas na requisição.

## 5. Pendência

- O `main` do servidor tem um merge local ainda **não enviado ao GitHub** (sem
  token de push na conta cPanel). Enquanto isso, cada `git pull` mescla
  automaticamente. Quando houver token, rodar `git push origin main` para alinhar.
