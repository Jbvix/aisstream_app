# Etapa 19 (Fase B) — Relatório operacional PDF/DOCX + compartilhamento

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo
Gerar **relatório operacional formatado** em **PDF e DOCX** com identidade KRATOS e
**compartilhar/baixar** o arquivo (mobile e desktop).

## Backend (`main.py`)
- `_build_report_payload()`: consolida dados reais — panorama (rebocadores SAAM com
  sinal, manobras programadas, concorrentes manobrando), **market share** (hoje/7d/
  30d), **frota SAAM** (manobras, horas em geofence, milhas) cruzada com **horas de
  operação/fadiga**, **meteoceânicas** (vento, maré, corrente, temperatura) e a
  **leitura do KRATOS** (insights).
- `_render_report_pdf()` (reportlab) e `_render_report_docx()` (python-docx):
  cabeçalho/seções, tabelas e rodapé com autoria; nome
  `KRATOS_Relatorio_AAAAMMDD_HHMM.{pdf,docx}`.
- Endpoint `POST /api/kratos/report-file` (`{format:"pdf"|"docx"}`) devolve o binário
  com `Content-Disposition`; alias `/dashboard/...`. Erros tratados (lib ausente →
  400 com mensagem). `Response` adicionado aos imports.
- `requirements.txt`: `python-docx` (PDF via reportlab já existente).

## Frontend
- **Mobile** (`index.html`): botão **Relatório** abre seletor **PDF/DOCX** → gera →
  **Web Share API** com arquivo (`navigator.share({files})`); fallback para download.
  Estado mostrado na faixa de conversa.
- **Desktop** (`dashboard.html`): botões **⬇ PDF** e **⬇ DOCX** no assistente —
  baixam (ou compartilham, onde suportado) o relatório.

## Validações
- `ast.parse(main.py)` e `node --check` (index/dashboard) → OK.
- Geração real: PDF (`%PDF`, ~3,5 KB) e DOCX (`PK`, abre no python-docx, 4 tabelas).
- Endpoint (TestClient): pdf/docx → 200 com Content-Type e filename corretos;
  formato inválido → 400. Visual do PDF conferido (identidade KRATOS, seções).

## Deploy (servidor)
- `git pull` + instalar dependência no virtualenv para o DOCX:
  `pip install python-docx` (o PDF já funciona sem isso). `touch tmp/restart.txt`.

## Arquivos alterados
- `main.py` — payload + renderizadores PDF/DOCX + endpoint; import de `Response`.
- `frontend/index.html` — botão Relatório (mobile) com seletor + share/download.
- `frontend/dashboard.html` — botões ⬇ PDF / ⬇ DOCX + manual.
- `requirements.txt` — `python-docx`.
