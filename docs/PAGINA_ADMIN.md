# Página do Administrador — Eficácia & Auditoria do KRATOS

Autor: Jossian Brito

Página restrita ao desenvolvedor/administrador para acompanhar a **evolução e a
eficácia** do KRATOS (provar que entrega valor) e **auditar** como ele está
sendo usado.

## Acesso

- URL: `https://tuglife.live/aisstream/admin`
- Protegida por **token** na variável de ambiente do servidor:

| Variável | Valor |
|----------|-------|
| `ADMIN_TOKEN` | um segredo forte definido por você (cPanel → Setup Python App → Environment variables) |

Sem `ADMIN_TOKEN` configurado, a página fica indisponível (seguro por padrão).
O token é informado na tela de entrada e fica só na sessão do navegador
(`sessionStorage`); é enviado no cabeçalho `X-Admin-Token`.

## Abas

### 1. Eficácia & Uso (O Número)
- Cartões: chats total / 24h / 7 dias, sessões de voz, **% útil (👍)**, quantos
  marcaram que **agiram**, taxa de feedback e **% "sem dado"**.
- Gráfico de **evolução do uso** (chats por dia, 14 dias).
- Gráfico de **temas mais consultados** (concorrente, manobra, frota, maré/vento,
  geofence/corredor, market share, distância/ETA).

### 2. Auditoria (conversas)
- Log das interações: data, tipo (chat/feedback/voz/erro), pergunta, prévia da
  resposta e flags (sem-dado, voz, útil/não, modo grok/local).
- Permite ver **como o KRATOS está sendo usado** e detectar discrepâncias
  (respostas fracas, temas fora de escopo, etc.).

### 3. Saúde & Resultado
- Cartões de saúde técnica: erros, "sem dado", voz configurada, usuário ativo.
- Tabela dos **últimos erros** (inclui falhas de voz/Grok com causa).
- **Correlação com resultado**: market share atual (fatia SAAM destacada) para
  cruzar uso do KRATOS com desempenho operacional.

### 4. Convites de acesso (acesso ao app por token)

Permite transformar o app (mapa + painel) em **acesso só por convite** e gerir os
convidados, com envio do link por **WhatsApp** ou **e-mail**.

**Gerar convite:** informe um **rótulo** (nome do convidado), escolha a **validade**
(7/30/90 dias ou sem expiração) e clique em *Gerar convite*. Cada convite produz um
**token** e um link de acesso `…/entrar?c=<token>`.

**Enviar:** por convite, os botões **WhatsApp** (abre `wa.me` com a mensagem e o
link prontos), **E-mail** (abre o cliente via `mailto:` preenchido) e **Copiar
link**. O envio parte do seu próprio aparelho/cliente (não há SMTP no servidor).

**Controles por convite:** status (ativo/expirado/revogado), validade, **último
acesso** (data e nº de acessos) e **Revogar** (corta o acesso na hora).

#### Como o convidado entra
- Abre o link recebido → a página `/entrar` valida o token e grava um **cookie**
  de sessão (HttpOnly), redirecionando ao app. Também é possível **colar o token**
  manualmente em `/entrar`.

#### Ativando o controle de acesso (importante)
- A trava só entra em vigor com a variável de ambiente **`ACCESS_CONTROL=on`** no
  servidor (cPanel → Setup Python App → Environment variables) + restart. **Por
  padrão vem desligada** — o deploy do código **não tranca** o site sozinho.
- Os convites **podem ser gerados antes** de ativar; a trava passa a exigi-los
  quando `ACCESS_CONTROL=on`.
- O **`ADMIN_TOKEN` é chave-mestra**: o dono sempre entra com
  `…/entrar?c=<ADMIN_TOKEN>` ou `…/?access=<ADMIN_TOKEN>` — sem risco de lockout.
- Exceções da trava: `/entrar`, `/api/access/*`, `/admin` e `/api/admin/*`.
- Limitação conhecida: o WebSocket de dados (AIS ao vivo) não é coberto pela trava
  HTTP; o acesso pelas páginas e APIs REST é. (Evolução futura, se necessário.)

| Variável | Efeito |
|----------|--------|
| `ACCESS_CONTROL` | `on` ativa o acesso só por convite (padrão: desligado) |

Endpoints: `GET/POST /api/admin/invites`, `POST /api/admin/invites/revoke`
(exigem `ADMIN_TOKEN`); `POST /api/access/validate`, `POST /api/access/logout`,
`GET /api/access/status` (públicos). Convites em
`data/users/<id>/access_invites.json` (local ao servidor, gitignored).

## Como os dados são coletados

- Telemetria automática a cada interação do chat e sessão de voz, gravada em
  `data/users/<id>/kratos_events.jsonl` (rolling, máx. ~5000 eventos, gitignored).
- Feedback do usuário: botão **"Isso foi útil? 👍/👎"** na última resposta do
  KRATOS no painel.
- Endpoints: `GET /api/admin/overview`, `GET /api/admin/conversations`
  (ambos exigem o token), `POST /api/kratos/feedback`.

## Privacidade

Os eventos guardam o que o usuário digita ao KRATOS (perguntas) e a prévia das
respostas, para fins de auditoria interna. Não há dados além dos já inseridos no
app. O arquivo é local ao servidor e não versionado.
