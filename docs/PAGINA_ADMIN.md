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
