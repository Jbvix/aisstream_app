# Tutorial — Sincronizar o KRATOS com o Obsidian (Supabase + Remotely Save)

Guia de configuração final (Sprint 4) da integração **KRATOS → Supabase Storage
→ Obsidian**. Ao terminar, o seu Obsidian terá um **grafo vivo** das manobras,
navios, berços, rebocadores e condições diárias da Baía de Guanabara.

> Arquitetura: o KRATOS (no cPanel) gera as notas Markdown e as envia para um
> bucket privado do Supabase. O plugin **Remotely Save**, no seu Obsidian
> (computador/celular), sincroniza esse bucket. Detalhes em
> `docs/PROPOSTA_OBSIDIAN_KRATOS.md`.

---

## Visão geral do fluxo

```
KRATOS (cPanel)  --upload REST-->  Supabase Storage  <--sync S3-->  Obsidian (Remotely Save)
```

- O backend usa a **REST API de Storage** (chave de serviço) para escrever.
- O Obsidian usa o **protocolo S3** (chaves S3) para sincronizar.
- As notas geradas ficam **sempre** sob a pasta `kratos/` do bucket.

---

## Passo 1 — Criar o bucket e as credenciais no Supabase

1. No painel do Supabase, vá em **Storage → New bucket**, crie um bucket
   **privado** chamado `kratos-vault`.
2. Em **Project Settings → API**, anote:
   - **Project URL** → `https://<project-id>.supabase.co`
   - Chave **`service_role`** (uso server-side; mantenha secreta).
3. Em **Storage → S3 Connection** (Settings), ative/clique em **New access key**
   e copie:
   - **Access Key ID** e **Secret Access Key** (são as chaves S3).
   - A **S3 Endpoint**: `https://<project-id>.supabase.co/storage/v1/s3`
   - A **Region** do projeto (ex.: `sa-east-1` ou `us-east-1`).

> Segurança: prefira as **chaves S3** (escopadas a Storage) à `service_role`
> sempre que possível. As chaves S3 vão para o celular — por isso o bucket
> **tem de ser privado**.

---

## Passo 2 — Configurar o KRATOS no servidor (cPanel)

No `.env` do servidor (veja `.env.example`), preencha:

```env
SUPABASE_URL=https://<project-id>.supabase.co
SUPABASE_KEY=<service_role>
SUPABASE_BUCKET=kratos-vault
OBSIDIAN_NOTE_PREFIX=kratos

# Opcional — sincronização automática (off por padrão):
OBSIDIAN_AUTO_SYNC=1
OBSIDIAN_AUTO_SYNC_SECONDS=300
```

Reinicie a app (`touch tmp/restart.txt`) e valide:

- **Diagnóstico:** abra `…/aisstream/api/obsidian/status` — deve mostrar
  `"configured": true` e o `bucket`/`prefix`.
- **Teste de conexão:** no Dashboard, seção **Integração Obsidian (Supabase)**,
  clique em **“Sincronizar Obsidian (Supabase)”**. A mensagem deve indicar
  *“Sincronizado: N/N notas enviadas”*. (Ou `POST …/api/obsidian/test-upload`
  para gravar só a nota de saúde.)

Confirme no Supabase que apareceu a pasta `kratos/` no bucket.

---

## Passo 3 — Instalar o Remotely Save no Obsidian

1. **Recomendado:** crie um **vault dedicado** ao KRATOS (ex.: “KRATOS”). Como o
   KRATOS **sobrescreve** as notas geradas a cada sincronização, um vault
   separado evita conflito com as suas anotações pessoais.
2. Em **Settings → Community plugins → Browse**, procure **Remotely Save**,
   instale e ative.

---

## Passo 4 — Configurar o Remotely Save

Em **Settings → Remotely Save**:

| Campo | Valor |
|-------|-------|
| **Sync Method** | `S3 or S3-compatible` |
| **Endpoint** | `https://<project-id>.supabase.co/storage/v1/s3` |
| **Region** | a região do seu projeto (ex.: `sa-east-1`) |
| **Bucket Name** | `kratos-vault` |
| **Access Key ID** | a chave S3 (Passo 1) |
| **Secret Access Key** | o segredo S3 (Passo 1) |
| **S3 URL style** | `Path-Style` (recomendado para Supabase) |

- Defina **Schedule for auto run** para **5 minutos**.
- Faça um **“Sync”** manual a primeira vez. As notas aparecerão sob a pasta
  `kratos/` do vault.

> Dica anti-conflito: **não edite** notas dentro de `kratos/` — elas são
> regeneradas pelo KRATOS. Suas anotações livres devem ficar **fora** dessa
> pasta.

---

## Passo 5 — Colorir o Graph View

Pressione `Ctrl + G` (Graph View) → **Groups** → **New group** e adicione:

| Query | Cor sugerida |
|-------|--------------|
| `tag:#kratos/rebocador/saam` | 🟢 Verde |
| `tag:#kratos/rebocador/concorrente` | 🔴 Vermelho |
| `tag:#kratos/manobra` | 🟣 Roxo |
| `tag:#kratos/navio` | 🔵 Azul |
| `tag:#kratos/berço` | 🟡 Amarelo |
| `tag:#kratos/empresa` | 🟠 Laranja |
| `tag:#kratos/dia` | ⚪ Cinza |

---

## Estrutura das notas geradas

Sob a pasta `kratos/` do bucket/vault:

```
kratos/
├── KRATOS.md            (índice / mapa de conteúdo)
├── manobras/            (uma nota por manobra)
├── navios/              (histórico + posição AIS atual)
├── bercos/              (manobras por berço)
├── rebocadores/         (SOG/COG/base — frota SAAM e concorrentes)
├── empresas/            (market share por EMP.RB)
├── dias/                (condição diária: vento + maré + manobras)
└── _sistema/health.md   (nota de teste de conexão)
```

### Tags emitidas
`#kratos/manobra` · `#kratos/manobra/saam` · `#kratos/manobra/concorrente`
· `#kratos/navio/comercial` · `#kratos/berço`
· `#kratos/rebocador/saam` · `#kratos/rebocador/concorrente`
· `#kratos/empresa/saam` · `#kratos/empresa/concorrente`
· `#kratos/dia` · `#kratos/indice`

---

## Casos de uso

- **Mapa estratégico vivo:** abra o Graph View e veja, por cor, onde a **SAAM
  (verde)** e os **concorrentes (vermelho)** estão atuando, e quais navios/berços
  concentram manobras.
- **Dossiê por navio:** abra a nota de um navio para ver todo o histórico de
  manobras e a posição AIS atual num só lugar.
- **Leitura do dia:** a nota `dias/AAAA-MM-DD` reúne **vento, maré e as manobras
  do dia** — útil para o briefing operacional.
- **Concorrência:** a nota da empresa (`empresas/WIL`, `empresas/CAM`) mostra o
  market share e as manobras associadas.
- **Mobilidade:** com o Remotely Save no celular, o dossiê viaja com você.

---

## Homologação (checklist)

- [ ] `…/api/obsidian/status` → `configured: true`.
- [ ] Botão **Sincronizar Obsidian** → “Sincronizado: N/N notas enviadas”.
- [ ] Pasta `kratos/` visível no bucket do Supabase.
- [ ] Remotely Save faz **Sync** sem erro e baixa a pasta `kratos/`.
- [ ] Graph View com grupos coloridos por tag.
- [ ] (Se `OBSIDIAN_AUTO_SYNC=1`) novas manobras aparecem após o intervalo
      configurado, sem ação manual.

---

## Solução de problemas

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| Botão diz “não configurado” | falta `SUPABASE_URL`/`KEY`/`BUCKET` no `.env` | preencher e reiniciar |
| HTTP 400/403 no upload | chave inválida ou bucket inexistente | revisar `service_role` e o nome `kratos-vault` |
| Remotely Save: erro de assinatura | endpoint/região/URL style incorretos | usar endpoint `/storage/v1/s3`, região do projeto, **Path-Style** |
| Notas não atualizam sozinhas | `OBSIDIAN_AUTO_SYNC` off ou dentro do debounce | ligar a flag / aguardar `OBSIDIAN_AUTO_SYNC_SECONDS` |
| Edições somem no Obsidian | editou nota dentro de `kratos/` | manter anotações livres fora de `kratos/` |
