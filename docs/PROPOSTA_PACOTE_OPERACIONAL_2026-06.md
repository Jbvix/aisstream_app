# PROPOSTA — Pacote Operacional KRATOS (reunião de 12/06/2026)

Autor: Jossian Brito

Status: **APROVADO (com ajustes)** · Data: 12/06/2026 · Aprovação: 15/06/2026

Proposta de implementação dos cinco pontos definidos em reunião, organizados em
etapas independentes (cada uma entra em produção sozinha). A ordem sugerida cria
primeiro a **central de alertas** (fundação) e encadeia as demais sobre ela.

---

## Visão geral

| # | Item da reunião | Etapa proposta | Esforço estimado |
|---|------------------|----------------|------------------|
| 2 | Alertas sonoros + popup configuráveis | **Etapa 14 — Central de Alertas** | 1 sessão |
| 1 | Controle de horas de operação (fadiga, 8 h/dia) | **Etapa 15 — Horímetro de operação** | 1–2 sessões |
| 4 | Navio na barra **sem contrato** de reboque | **Etapa 16 — Radar de oportunidade** | 1 sessão |
| 3 | Corredores por **GPX** (derrotas) com **XTE** | **Etapa 17 — Derrotas GPX + XTE** | 1–2 sessões (aguarda arquivos) |
| 5 | Upload de arquivo no chat (conhecimento) | **Etapa 18 — Conhecimento por arquivo** | 1–2 sessões |

A Etapa 14 vem primeiro porque os itens 1 e 4 disparam alertas — com a central
pronta, cada nova detecção é só "mais um tipo de alerta".

---

## Etapa 14 — Central de Alertas (sonoro + popup) 🔔

**Objetivo:** o usuário escolhe o que quer ser avisado; o app toca som e mostra
popup no momento do evento.

**Como funciona:**
- **Backend — barramento de eventos:** os detectores que já rodam (entrada em
  geofence, programação, frota) passam a publicar eventos de alerta no WebSocket
  já existente (`{type:"alert", kind, severity, title, message, vessel}`), com
  deduplicação (não repetir o mesmo alerta da mesma embarcação em N minutos).
- **Frontend — central no mapa:** botão 🔔 abre o painel de preferências:
  liga/desliga **por tipo de alerta**, volume e teste de som. Preferências
  persistidas por usuário. Ao chegar alerta ativo: **som** (tons distintos por
  severidade, via Web Audio — sem depender de arquivos), **popup/toast** no app
  (empilhável, com hora e botão "ver no mapa" que centraliza na embarcação) e,
  se o usuário permitir, **notificação do navegador** (aparece mesmo com a aba
  em segundo plano).
- **Tipos de alerta no lançamento:**
  1. **Entrada de navio na barra** (pedido da reunião) — navio mercante cruzando
     a geofence da barra/canal de acesso da BG;
  2. Concorrente (WIL/CAM) entrando em geofence de manobra;
  3. Rebocador da frota sem sinal AIS (possível barra fora);
  4. POB de manobra SAAM se aproximando (30 min);
  5. (Etapas 15 e 16 acrescentam os seus.)
- **Geofence "Barra da BG":** se ainda não houver, criamos juntos no mapa (a
  ferramenta de desenho já existe) — a detecção usa a geofence nomeada.

**Limite conhecido:** navegadores só tocam som após a primeira interação do
usuário com a página (clique). O painel 🔔 já resolve isso na ativação.

**Critério de aceite:** com o alerta "entrada na barra" ligado, um navio cruzando
a geofence da barra gera som + popup em até ~5 s, e o popup centraliza o mapa
nele ao clicar.

---

## Etapa 15 — Horímetro de operação do rebocador (fadiga, 8 h/dia) ⏱️

**Objetivo:** controlar as horas de operação de cada rebocador no dia, com limite
de segurança de **8 h**, segundo o ciclo definido na reunião:

> repouso → saída → manobra → pós-manobra → navegação para qualquer ponto →
> chegada → **repouso**. Navegação de um ponto a outro **conta** como operação.

**Como funciona:**
- **Máquina de estados por rebocador** (backend, sobre o AIS já recebido):
  - **Em operação:** começa quando o rebocador sai do repouso (SOG sustentado
    acima do limiar de movimento — proposta: ≥ 0,5 kn por ≥ 3 min, reaproveitando
    a histerese já existente no mapa).
  - **Repouso:** parado (SOG < 0,5 kn) por tempo contínuo — proposta: **≥ 15 min**
    — em **qualquer ponto** (base, fundeio ou cais). Pausas curtas entre fainas
    (esperando navio, por ex.) continuam contando como operação.
  - O tempo em operação acumula no **dia operacional** (proposta: 00h–24h local,
    com histórico diário guardado).
- **Persistência:** `data/users/<id>/tug_operating_hours.json` (sobrevive a
  restart), com histórico de 30 dias por rebocador.
- **Painel Frota SAAM:** barra de progresso por rebocador — **verde** < 6 h,
  **âmbar** 6–8 h, **vermelho** ≥ 8 h — com horas/minutos do dia e botão de
  histórico (7/30 dias).
- **Alertas (via Etapa 14):** ao atingir **7 h** (aviso de planejamento) e
  **8 h** (limite atingido — severidade alta).
- **KRATOS ciente:** as horas do dia entram no contexto operacional — ao sugerir
  alocação, o KRATOS passa a considerar fadiga ("o PX já tem 7h20 hoje; para a
  manobra das 19h, prefira o LT").

**Pontos a validar com você (defaults propostos):**
- Reset do dia: meia-noite local (alternativa: janela móvel de 24 h).
- Parado por **15 min** = repouso (ajustável).
- Limite 8 h fixo para todos (ou configurável por rebocador?).

**Critério de aceite:** acompanhar um dia real e o total por rebocador refletir o
ciclo (transitos contam; espera parada > 15 min não conta); alertas de 7 h/8 h
disparando; KRATOS citando as horas quando perguntado.

---

## Etapa 16 — Radar de oportunidade: navio na barra SEM contrato 🎯

**Objetivo:** alertar quando um navio entra na barra **sem manobra programada com
nenhuma empresa de reboque** — alvo comercial direto.

**Como funciona:**
- Ao detectar navio mercante (carga/petroleiro/passageiros — LOA mínima proposta:
  **90 m**) entrando na barra/BG, o backend cruza o nome (normalizado, como já é
  feito) com a **programação da Praticagem**:
  - **Tem manobra com EMP.RB** (SAA/WIL/CAM) → tráfego normal, sem alerta;
  - **Não tem manobra na janela de ±24 h** → marca **"SEM CONTRATO (oportunidade)"**.
- **No mapa:** destaque visual próprio (anel âmbar pulsante, distinto do vermelho
  de concorrente) + entrada na lista "Oportunidades" (painel lateral).
- **Alerta** (via Etapa 14) com severidade comercial: nome, tipo, LOA, destino
  aparente (rumo/geofence) e botão "ver no mapa".
- **KRATOS ciente:** lista de oportunidades no contexto — "há 2 navios na barra
  sem contrato agora: X (graneleiro, 225 m) e Y (tanque, 180 m)".

**Honestidade técnica:** o navio pode ter contrato fechado e ainda não publicado
na programação (falso positivo) — por isso o rótulo é "oportunidade", não
certeza; o alerta vale como gatilho comercial para verificação humana.

**Pontos a validar:** LOA mínima (90 m?), janela de matching (±24 h?), categorias
incluídas.

**Critério de aceite:** navio real entrando na barra sem manobra na programação
gera alerta + destaque + aparece na resposta do KRATOS quando perguntado.

---

## Etapa 17 — Corredores de tráfego por GPX (derrotas) com XTE 🗺️

**Objetivo:** importar os arquivos **GPX de derrotas** (waypoints) da Baía de
Guanabara e transformá-los em **corredores de tráfego com largura** (XTE — limite
de afastamento lateral da via), mostrando as vias de navegação seguras no mapa.

**Como funciona:**
- **Importação GPX:** no painel Geofences do mapa, botão **"Importar GPX"** —
  aceita rotas (`<rte>`) e trilhas (`<trk>`); cada derrota vira um **corredor
  nomeado** (nome vindo do GPX, editável).
- **XTE / largura da via:** ao importar, define-se o XTE (proposta padrão:
  **0,05 NM ≈ 93 m para cada bordo**, ajustável por corredor). O mapa desenha a
  **faixa** (linha central + buffer de largura real em escala) — vias de segurança
  visíveis sobre a carta.
- **Usos imediatos:**
  1. **Distância/ETA pela derrota** (em vez de linha reta) — o KRATOS já avisa
     que a linha reta subestima; com as derrotas oficiais, passa a calcular pela
     via;
  2. **Alerta de fora da via** (via Etapa 14, opcional): rebocador da frota com
     afastamento lateral acima do XTE do corredor;
  3. **KRATOS:** raciocina e cita as derrotas pelo nome.
- **Compatibilidade:** os corredores desenhados à mão continuam funcionando; o
  GPX é uma segunda forma de criar (mais precisa).

**Dependência:** aguardando os **arquivos GPX**. A importação genérica pode ser
construída antes e validada no momento em que os arquivos chegarem.

**Critério de aceite:** importar um GPX real → corredor com largura correta no
mapa; ETA de um rebocador calculado pela derrota; KRATOS citando a via.

---

## Etapa 18 — Upload de arquivo no chat (retenção de conhecimento) 📎

**Objetivo:** botão de **carregar arquivo** na caixa de diálogo do KRATOS — o
conteúdo é retido e passa a fazer parte do conhecimento aplicado nas respostas
(como fizemos com as normas NPCP, mas self-service).

**Como funciona:**
- **No chat (painel):** botão 📎 ao lado do campo de mensagem — aceita **PDF,
  TXT e MD** (DOCX em fase 2, se necessário). Limite proposto: **15 MB**.
- **Backend:** extrai o texto (PDF via PyMuPDF, já disponível no servidor),
  guarda em `data/users/<id>/knowledge/` com metadados (nome, data, tamanho,
  resumo) — gitignored.
- **Aplicação do conhecimento (em duas camadas):**
  1. **Índice no prompt:** o KRATOS sempre sabe **quais documentos existem**
     (título + resumo de cada um);
  2. **Trechos relevantes por pergunta:** busca por palavras-chave da pergunta
     nos documentos e injeta os trechos que casam (teto de caracteres por
     resposta, para não estourar o contexto). Documentos pequenos (< ~8 mil
     caracteres) entram inteiros.
- **Gestão:** lista dos documentos carregados no painel (nome, data, tamanho)
  com botão **remover**; o KRATOS confirma no chat o que absorveu ("Recebi o
  documento X — 12 páginas sobre tarifas de praticagem; já estou considerando").
- **Voz ao vivo:** o índice + resumos entram nas instruções da sessão de voz
  (trechos completos só no chat de texto, por limite de tamanho do prompt).

**Critério de aceite:** subir um PDF de teste pelo chat → KRATOS responde
pergunta cujo conteúdo só existe no documento; remover o arquivo → conhecimento
some.

---

## Ordem, dependências e entregas

```
Etapa 14 (alertas)  ──┬─→ Etapa 15 (horímetro usa alertas)
                      ├─→ Etapa 16 (oportunidade usa alertas)
                      └─→ Etapa 17 (fora-da-via usa alertas; aguarda GPX)
Etapa 18 (conhecimento) — independente, pode ser paralela
```

- Cada etapa: branch → testes → commit → fast-forward `main` → deploy → relatório
  em `docs/relatorios/` e Manual do usuário atualizados (padrão do projeto).
- **Sugestão de início:** Etapas 14 + 16 juntas (mesma região de código — barra/
  geofences/eventos), depois 15, 18 e, quando os GPX chegarem, 17.

## Decisões que preciso de você (com os defaults que aplico se aprovar como está)

| # | Decisão | Default proposto |
|---|---------|------------------|
| 1 | Reset do horímetro | Meia-noite local (dia operacional 00h–24h) |
| 2 | Parado por quanto tempo = repouso | 15 min com SOG < 0,5 kn |
| 3 | Marcos de alerta de fadiga | 7 h (aviso) e 8 h (limite) |
| 4 | LOA mínima p/ "sem contrato" | 90 m |
| 5 | Janela de matching c/ programação | ±24 h |
| 6 | XTE padrão dos corredores GPX | 0,05 NM por bordo (ajustável) |
| 7 | Formatos de upload | PDF, TXT, MD (15 MB) |

## Decisões finais (aprovação de 15/06/2026)

A proposta foi **aprovada com os seguintes ajustes** sobre os defaults:

| # | Decisão | Valor aprovado |
|---|---------|----------------|
| 2 | Repouso (Etapa 15) | **8 h** (semântica exata do ciclo a confirmar na Etapa 15) |
| 4 | LOA mínima p/ "sem contrato" (Etapa 16) | **120 m** |
| — | Escopo do radar (Etapa 16) | **Apenas navios mercantes** — **excluir embarcações offshore** (PSV/AHTS/supply) |
| 1, 3, 5, 6, 7 | Demais defaults | Mantidos como propostos |

Execução iniciada pelas **Etapas 14 (Central de Alertas) + 16 (Radar de
oportunidade)**, por compartilharem a região de código (barra/geofences/eventos).


## Progresso da execução

- ✅ Etapa 14 — Central de Alertas (09aa…/main)
- ✅ Etapa 16 — Radar de oportunidade
- ✅ Etapa 18 — Upload de conhecimento no chat
- ✅ Etapa 15 — Horímetro de operação (fadiga)
- ⏳ Etapa 17 — Corredores por GPX + XTE (aguardando arquivos GPX)
