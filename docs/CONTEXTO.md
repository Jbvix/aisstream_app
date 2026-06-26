# CONTEXTO — KRATOS (context pack do projeto)

Autor: Jossian Brito

Documento-semente para **reidratar o raciocínio do projeto** em qualquer momento
(nova sessão de IA, novo desenvolvedor, ou base para um novo aplicativo). Leia
este arquivo + os ADRs em `docs/adr/` para retomar o "porquê" das decisões.

> Atalho para a IA: "Leia `docs/CONTEXTO.md`, os ADRs em `docs/adr/` e os
> relatórios recentes em `docs/relatorios/` antes de começar."

## 1. O que é
**KRATOS — Inteligência Naval Estratégica.** App de monitoramento AIS do Porto do
Rio de Janeiro / Baía de Guanabara (BG). Mostra embarcações em tempo real, detecta
eventos operacionais (entrou na barra, saiu do fundeio, atracou…), dá alertas,
relatórios e um assistente (texto/voz) que conhece as normas locais (NPCP-RJ).

- **Produção:** `https://tuglife.live/aisstream/` (cPanel, deploy via `git pull`).
- **Posicionamento atual:** serviço **operacional neutro** para Praticagem e apoio
  portuário (ver `pitch/` — material comercial, não versionado).

## 2. Stack e topologia
- **Backend:** FastAPI (ASGI) em `main.py` (flat, ~4k linhas).
- **Frontend:** estático em `frontend/` (`index.html` mapa Leaflet; `dashboard.html`
  painel; `graph.html` grafo; `admin.html`; `entrar.html`; `versao.html`).
- **Hospedagem:** cPanel + **Phusion Passenger** + **a2wsgi** (ASGI→WSGI). Montado
  sob o subcaminho **`/aisstream`** (`SCRIPT_NAME`/`root_path`).
- **Dados de runtime:** arquivos JSON em `data/users/<id>/...` (gitignored).
- **Externos:** AISStream (AIS), xAI Grok (chat + voz Leo Realtime), Open-Meteo
  (clima/maré/corrente), Supabase (Obsidian, opcional).

## 3. Decisões-chave (resumo — detalhes nos ADRs)
- **WSGI/Passenger não faz WebSocket** → produção usa **polling** (`/api/vessels`).
  `tuglife.live` está em `FORCE_POLLING_HOSTS`. → ADR 0002.
- **Subcaminho `/aisstream`** exige tratar `root_path` em redirects/cookies. → ADR 0003.
- **Acesso por convite (token)**, não login/senha; `ADMIN_TOKEN` é chave-mestra;
  `ACCESS_CONTROL` desligado por padrão (kill-switch). → ADR 0004.
- **Conhecimento do KRATOS vive no prompt** (constantes `KRATOS_*` em `main.py`),
  com foco na BG. → ADR 0005.
- **Anti-flicker dos alvos:** ícone só recria quando a *assinatura* muda; rumo
  congela em parado; sem dupla contagem. → ADR 0006.

## 4. Convenções de trabalho (de `CLAUDE.md`)
1. **Atualizar o manual** (`frontend/dashboard.html`, bloco `.manual-modal__body`) a
   cada mudança visível.
2. **Validar sintaxe** antes de commit: `python3 -c "import ast; ast.parse(open('main.py').read())"`
   e `node --check` no script do HTML alterado.
3. Fluxo git: branch de trabalho → commit → fast-forward de `main` → deploy puxa de `main`.
4. **Relatório por etapa** em `docs/relatorios/` (`AAAA-MM-DD-etapa-NN-<slug>.md`).
5. **Autoria:** `Autor: Jossian Brito` em todo `.md`.
- **SAA = SAAM** (campo EMP.RB da Praticagem); WIL e CAM = concorrentes.

## 5. O que está pronto (junho/2026)
Mapa AIS + alvos em escala real · geofences/corredores · eventos (barra/BG) ·
maré/vento/corrente/temperatura · Central de Alertas (som/popup/notificação) ·
radar de oportunidade · horímetro de fadiga · assistente texto+voz · conhecimento
NPCP-RJ (foco BG) · upload de conhecimento no chat · relatórios PDF/DOCX +
compartilhar · UI mobile + Dynamic Voice Orb · acesso por convite · grafo 2D/3D ·
painel de implementações (`/versao`).
Ver painel: `docs/KRATOS_painel_implementacoes.png` e relatórios das etapas 01–19.

## 6. Pendências / próximas
- **Etapa 17 — Corredores por GPX/XTE** (aguardando arquivos de derrotas).
- Oportunidades para apoio/rebocadores e **lanchas de prático** (ver `pitch/` e
  `docs/relatorios/`/matriz de oportunidades).

## 7. Glossário do domínio
- **AIS**: sinal de posição transmitido pelas embarcações. **MMSI**: id da embarcação.
- **POB** (Pilot On Board): horário de embarque do prático. **PEP**: Ponto de Espera
  de Prático. **Atalaia**: central de coordenação da Praticagem (VHF 12).
- **NPCP-RJ**: Normas e Procedimentos da Capitania dos Portos do RJ. **ZP-15**: zona
  de praticagem. **TTE**: tonelada de tração estática (bollard pull) do rebocador.
- **Geofence**: área monitorada (berço, base, fundeadouro, barra). **Corredor**:
  rota navegável nomeada. **Fundeio**: ancoradouro.
- **SAAM (SAA)**: nossa empresa de reboque; **WIL/CAM**: concorrentes.

## 8. Para iniciar um NOVO app (reaproveitando este)
1. Use o **"KRATOS Core"** já extraído em `core-template/` (ver
   `docs/adr/0007-estrategia-de-reuso-multi-repo.md`). Copie a pasta como raiz
   do novo repo e preencha os marcadores `TODO-DOMINIO`.
2. Crie `CLAUDE.md` e `docs/CONTEXTO.md` próprios do novo app (copie este como base).
3. Mantenha a convenção de **ADRs + relatórios** desde o 1º dia.
4. Reaproveite genéricos: esqueleto FastAPI+estático, splash, acesso por convite,
   Central de Alertas, geração de relatório PDF/DOCX, Dynamic Voice Orb.
   Reescreva o **domínio** (geofences, normas, eventos específicos).
