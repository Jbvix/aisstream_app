# UI/UX — barra do grafo, toolbar do assistente (ícones+ajuda), ocultar Obsidian

Autor: Jossian Brito

Data: 2026-06-15

## 1) Grafo Estratégico — barra superior organizada/centralizada (`graph.html`)
- Header com `flex-wrap` + `justify-content:center` (centraliza e quebra bem em
  telas estreitas). Em ≤720px o título ocupa a 1ª linha centralizado e os botões
  ficam centralizados abaixo.
- A contagem **"N nós · N conexões · 2D/3D"** (`#status`) saiu de elemento
  flutuante (que colidia com o header) para um **chip dentro do header**.
- A `.meta` (texto "Manobra ↔ Navio ↔ …"), redundante com a **Legenda**, é
  **ocultada no mobile**.

## 2) Assistente (dashboard) — toolbar em ícones + ajuda, centralizada
- Botões principais viraram **ícones** com tooltip/aria: 💬 Conversar · 📎 Anexar ·
  🎧 Voz ao vivo · 🎙️ Falar · 🔊 Voz · **❓ Ajuda**.
- **❓ Ajuda** abre uma caixa explicando o que cada botão faz.
- Os botões de saída (Gerar relatório, ⬇PDF, ⬇DOCX, Gerar insights, Limpar
  conversa) permanecem como texto, após um separador.
- A barra agora é **centralizada** (`justify-content:center`).
- JS dos estados atualizado para alternar só o ícone (▶ 🎧/⏹/…, 🔊/🔇, 🎙️/🔴),
  preservando handlers e `aria-pressed`.

## 3) Integração Obsidian (Supabase) — oculta
- A seção foi **ocultada** (`display:none`) no dashboard. Os scripts/IDs
  permanecem no DOM (sem quebrar JS); pode ser reativada removendo o `display:none`.

## Validações
- `node --check` nos scripts de `dashboard.html` e `graph.html` → OK.
- IDs conferidos (`#status` único no grafo; `btnHelp`/`assistantHelp` no dashboard).

## Arquivos alterados
- `frontend/graph.html` — header centralizado + `#status` como chip + `.meta` mobile.
- `frontend/dashboard.html` — toolbar em ícones + ajuda + centralização; Obsidian oculto.
