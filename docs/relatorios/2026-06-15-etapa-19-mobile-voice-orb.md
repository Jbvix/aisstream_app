# Etapa 19 (Fase A) — UI mobile compacta + Dynamic Voice Orb

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo
Tela de celular simples e focada (mapa + voz), com **Dynamic Voice Orb** central,
barra inferior de ações e a conversa do KRATOS acima. Desktop inalterado.
(Proposta aprovada: barra = Mapa · Alertas · Relatório · Painéis; começar pelo
mobile/Orbe; relatórios PDF+DOCX virão na Fase B.)

## O que foi implementado (`frontend/index.html`)
- **Camada mobile isolada** (`#mobileShell`), ativada só em `@media (max-width:768px)`;
  no celular oculta o dock lateral, a caixa de insights e a legenda; o desktop
  permanece intacto (`@media (min-width:769px)` força ocultar).
- **Barra inferior** fixa com 4 ações (Mapa→Filtros, Alertas→Central de Alertas,
  Relatório→compartilhar, Painéis→bottom-sheet com Frota/Geofences/Tempo/SAAM/
  Entrada-Saída/Área/Filtros/Status) e o **Orbe de Voz central elevado**.
- **Dynamic Voice Orb** (canvas + requestAnimationFrame, não desenha quando oculto):
  estados **repouso/ouvindo/processando/falando** com cor e animação distintas,
  derivados dos callbacks de voz (`onStateChange`, `onUserText`, `onAssistantText`,
  `onAssistantInterrupted`). Toque inicia/encerra a voz ao vivo (reusa
  `getMapLiveVoice`).
- **Faixa de conversa** mobile acima da barra: transcrição (usuário/KRATOS) +
  estado atual; aparece ao ativar a voz.
- **Badge de alertas** espelhado no botão Alertas do mobile.
- **Relatório (v1):** compartilha o resumo (insights) via **Web Share API**
  nativa, com fallback de cópia para a área de transferência. (PDF/DOCX
  formatado = Fase B.)

## Validações
- `node --check` em index.html e dashboard.html → OK.
- IDs do mobile shell conferidos; Orbe não desenha no desktop (guarda
  `canvas.offsetParent`).

## Pendente (Fase B)
- Relatório **formatado em PDF e DOCX** (reportlab + python-docx) com identidade
  KRATOS e **compartilhamento do arquivo** (Web Share files / download).

## Arquivos alterados
- `frontend/index.html` — CSS/HTML/JS da UI mobile + Voice Orb; hooks de voz.
- `frontend/dashboard.html` — Manual (seção "No celular").
