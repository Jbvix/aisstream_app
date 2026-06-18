# PROPOSTA — UI mobile compacta com Dynamic Voice Orb + relatórios (DOCX/PDF)

Autor: Jossian Brito

Status: **AGUARDANDO APROVAÇÃO** · Data: 2026-06-15

Mockup: `docs/mockups_mobile_voice_orb.png`

## Objetivo
Criar uma experiência **mobile dedicada** (celular), simples e focada em **mapa +
voz**, com um **Dynamic Voice Orb** central, barra inferior de ações e a conversa
do KRATOS logo acima. O **desktop permanece exatamente como está**. Incluir
**geração de relatórios formatados (DOCX/PDF)** com **botão de compartilhamento**.

## Layout mobile (≤ 768px)
- **Mapa em tela cheia** (foco total na situação).
- **Header minimal:** logo KRATOS + chips condensados (maré ⌃ / vento / corrente /
  temperatura). Sem o dock lateral do desktop.
- **Faixa de conversa** (acima da barra): transcrição ao vivo do KRATOS + estado
  ("ouvindo…", "processando…", "falando").
- **Barra inferior** com 4 ações + o **Orbe de voz central destacado** (elevado,
  estilo "notch/FAB"):
  - **Mapa** (camadas/filtros), **Alertas** (🔔), **[ORBE DE VOZ]**, **Relatório**, **Painéis** (acesso ao resto: frota, geofences, tempo, SAAM…).

## Dynamic Voice Orb (estados)
Esfera fluida que muda **cor e animação** conforme o estado da IA (derivado dos
callbacks já existentes em `kratos-voice.js`: `onStateChange`, `onUserText`,
`onAssistantText`):

| Estado | Visual | Quando |
|---|---|---|
| **Repouso** | azul calmo, leve respiração | inativo — toque para falar |
| **Ouvindo** | ciano pulsante (ondas para fora) | captando sua voz |
| **Processando** | giro âmbar+ciano | pensando/gerando |
| **Falando** | dourado com ondas no ritmo da fala | KRATOS respondendo |

Implementação: **Canvas/SVG animado** leve (sem libs pesadas), com `prefers-reduced-motion`
respeitado. Toque no orbe inicia/encerra a conversa por voz ao vivo.

## Relatórios formatados (DOCX/PDF) + compartilhamento
- Botão **Relatório** → gera o relatório executivo do KRATOS (já existe o conteúdo)
  e **exporta formatado**:
  - **PDF** com identidade KRATOS (capa/cabeçalho, seções, market share, frota,
    metocean) — via `reportlab` (já instalado).
  - **DOCX** com a mesma estrutura — via `python-docx` (a adicionar ao
    `requirements.txt`; instalar no servidor).
- **Compartilhar:** botão usa a **Web Share API** nativa do celular (abre a folha
  de compartilhamento → WhatsApp, e-mail, etc.) enviando o arquivo; **fallback**
  para download direto onde a API não houver.
- Backend: endpoint `POST /api/kratos/report-file` (formato pdf|docx) → devolve o
  arquivo; o app dispara o share/download.

## Técnico
- **Sem afetar o desktop:** todo o layout mobile vive sob `@media (max-width: 768px)`
  + um container mobile próprio; o dock/painéis do desktop ficam ocultos no celular
  e reaproveitados via "Painéis".
- Reaproveita o motor de voz, alertas, clima e relatório já existentes.
- Performance: orbe em `requestAnimationFrame` só quando ativo/visível.

## Decisões para aprovação (defaults propostos)
| # | Decisão | Default |
|---|---------|---------|
| 1 | Botões da barra inferior | Mapa · Alertas · **Orbe** · Relatório · Painéis |
| 2 | Formato do relatório | **PDF e DOCX** (escolha no botão) |
| 3 | Compartilhamento | Web Share API nativa + fallback download |
| 4 | Breakpoint mobile | ≤ 768px (ativa layout compacto) |
| 5 | Conteúdo do relatório | panorama, market share, concorrentes, frota/fadiga, metocean, recomendações |

Aprovando (no todo ou com ajustes), implemento em duas frentes: **(A) layout mobile
+ Orbe** e **(B) relatório DOCX/PDF + compartilhar**.
