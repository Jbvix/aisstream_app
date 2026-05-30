# Proposta de Evolução — Projeto AISStream / KRATOS

> Documento de proposta. Objetivo estratégico: ganho de *market share* e
> antecipação dos movimentos dos rebocadores da concorrência no Porto do Rio
> de Janeiro / Baía de Guanabara, com um assistente proativo chamado **KRATOS**.
>
> Hospedagem atual: cPanel — `https://tuglife.live/aisstream/` (Aplicação Web
> Python + Passenger WSGI, deploy via Git Version Control).

---

## 1. Diagnóstico do que já existe hoje

O projeto está mais maduro do que aparenta. Fundação de dados sólida.

**Backend (`main.py`, ~2.569 linhas — FastAPI):**
- Relay WebSocket de dados AIS em tempo real (modo `live` via AISStream + modo `mock`).
- Sistema de **geofences** (berço, polígono, base de rebocador) com detecção de entrada/saída.
- Contagem de **manobras por rebocador SAAM** + horas dentro de geofence + milhas náuticas (Haversine).
- **Market share** por `EMP.RB` com janelas (hoje / 7 dias / 30 dias).
- Scraper da **Praticagem-RJ** (`praticagem_saa.py`) — lê tabela de programação (POB) e fila "Navios na Pedra".
- **Monitor de alterações** da programação (atrasos, adiantamentos, simultaneidade).
- Integração de **vento** via Open-Meteo (maré ainda é placeholder).
- **Assistente Grok/xAI** (`_ask_grok_with_context`) com perfis (executivo/operacional/despacho/híbrido) e **memória de aprendizado** (`strategy_memory.json`).
- Identificação de **concorrentes** por MMSI (WIL, CAM).

**Frontend:**
- `index.html` (~3.347 linhas) — mapa Leaflet ao vivo com posições, legendas, painéis flutuantes, vento.
- `dashboard.html` (~974 linhas) — geofences, manobras SAA, frota SAAM, market share, assistente, monitor.

**Conclusão:** o que falta é **transformar dados em antecipação** e dar ao
produto uma **identidade (KRATOS)** com UX que comunique "estou um passo à frente".

---

## 2. Visão central: nasce o KRATOS

Hoje o assistente é um campo de texto "Consultar Grok". A proposta é elevá-lo a
**agente persistente e proativo** — não um chatbot que espera pergunta, mas um
**copiloto estratégico** que observa o porto continuamente e *fala primeiro*.

> **KRATOS** = camada de inteligência que cruza maré + vento + entradas/saídas +
> geofences + posição dos rebocadores concorrentes e **emite alertas e
> oportunidades antes do operador perguntar.**

Princípio de produto: **"O resultado pode não vir, mas a presença é
inegociável."** A interface deve sempre demonstrar vigilância ativa.

---

## 3. Melhorias de UX / UI

### 3.1 Identidade e presença do KRATOS
- **Barra/HUD KRATOS** fixa no topo do mapa: avatar/ícone + status "🟢 Vigiando · última leitura há 12s" + contador de embarcações monitoradas.
- **Pulso de atividade**: micro-animação discreta a cada varredura ("scan" do porto) reforçando que ele está atento.
- **Feed de eventos KRATOS** (timeline lateral): "Concorrente WIL entrou no berço X", "Janela de manobra livre às 14h30", "Vento subindo — reforço recomendado".

### 3.2 Centro de alertas proativos
- Badge de notificações com **níveis** (info / oportunidade / risco).
- **Cards de oportunidade**: "Navio Y chega 16h, nenhum rebocador concorrente posicionado → janela tua". Botão "Marcar interesse".
- Toasts não-intrusivos + opção de som para eventos críticos.

### 3.3 Mapa mais legível
- **Trilhas (rastros)** das embarcações nos últimos N minutos para leitura de intenção.
- **Heatmap de disputa** por geofence (onde a concorrência mais atua).
- Cores consistentes por empresa (frota própria vs. WIL vs. CAM).
- **Modo "Foco"**: clicar num navio destaca rebocadores próximos + ETA + manobra prevista.

### 3.4 Dashboard reorganizado
- Topo: **placar do dia** (manobras próprias vs. concorrência, market share hoje, oportunidades abertas).
- Layout em cards responsivos, tema escuro náutico (já existe a base de cores), tipografia tabular para números.
- Exportação de **relatório PDF/CSV** (já listado como próximo passo no doc do assistente).

### 3.5 Mobile / campo
- Versão responsiva enxuta para o operador acompanhar do celular (só placar + alertas + mapa).

---

## 4. Inteligência estratégica (o coração do pedido)

### 4.1 Motor de previsão de movimentação
- Cruzar **POB da praticagem** + **velocidade/rumo AIS** + **maré/vento** → estimar **janela real de manobra** de cada navio.
- Detectar **padrões de aproximação** de rebocadores concorrentes (ele está indo posicionar para a manobra das 15h?).
- **ETA preditivo** por navio até o berço/fundeio.

### 4.2 Detector de oportunidades
Regras + Grok analisando: navios sem rebocador concorrente posicionado, janelas
onde a concorrência está saturada (manobras simultâneas), trechos onde o
posicionamento atual dá vantagem — **sem comprometer a própria programação** (o
motor checa conflito com as manobras já agendadas).

### 4.3 KRATOS proativo (xAI Grok)
- **Loop de fundo**: a cada ciclo, KRATOS recebe o snapshot e decide se há algo digno de alertar (não só responde — ele inicia).
- **Briefing automático** no início do turno e ao detectar mudança relevante.
- **Maré real**: integrar fonte oficial (DHN/Marinha ou tábua de marés do RJ) — hoje é placeholder.
- **Score de confiança** por recomendação (já sugerido no roadmap interno).

### 4.4 Memória e aprendizado
- Expandir `strategy_memory.json`: registrar acertos/erros das previsões para o KRATOS calibrar (feedback loop).

---

## 5. Roadmap em fases

| Fase | Entrega | Foco |
|------|---------|------|
| **0 — Pipeline** | Configurar **pull GitHub → cPanel** (Pull or Deploy) + restart do app Python | Deploy confiável |
| **1 — Identidade KRATOS** | HUD de presença, feed de eventos, rebranding do assistente | UX / percepção |
| **2 — Alertas proativos** | Centro de alertas + loop de fundo do KRATOS + toasts | Antecipação |
| **3 — Previsão** | Motor ETA + janelas de manobra + detector de oportunidade | Estratégia |
| **4 — Dados ricos** | Maré oficial, trilhas no mapa, heatmap, score de confiança | Profundidade |
| **5 — Relatórios** | PDF/CSV executivo, placar do dia, mobile | Gestão / market share |

---

## 6. Riscos / pontos de atenção
- **Segredos expostos**: `AISSTREAM_API_KEY` e `XAI_API_KEY` ficam só como env vars no cPanel (correto) — garantir que **nunca** entrem no Git.
- **Scraping da praticagem**: site pode mudar HTML; tratar com tolerância a falha (já há fallback).
- **cPanel/Passenger**: app é long-running com WebSocket — validar se o Passenger mantém o worker AIS vivo (verificar no deploy).
- **Limites de chamada xAI**: loop proativo deve ter throttle para não estourar custo.

---

## 7. Próximos passos imediatos

1. **Esta proposta** (concluída — este documento)
2. **Configurar o pull GitHub → cPanel** (aba *Pull or Deploy*) — ver `DEPLOY_PULL_CPANEL.md`
3. **Iniciar a Fase 1** (identidade KRATOS) como primeira melhoria visível
