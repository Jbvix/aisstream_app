# Etapa 18 — Upload de arquivo no chat (retenção e aplicação de conhecimento)

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo

Disponibilizar, na caixa de diálogo do KRATOS, a opção de **carregar arquivo**
para retenção e aplicação de conhecimento — o conteúdo passa a influenciar as
respostas (como as normas NPCP, mas self-service).

## Decisões técnicas
- **Sem `python-multipart`** (não disponível no ambiente): o upload é feito por
  **JSON + base64**, evitando nova dependência na camada web e funcionando no
  cPanel de imediato.
- **PDF** extraído com **PyMuPDF** (import tardio; adicionado ao `requirements.txt`).
  TXT/MD funcionam mesmo sem PyMuPDF; PDF sem a lib retorna erro claro.

## O que foi implementado

### Backend (`main.py`)
- Armazenamento por usuário em `data/users/<id>/knowledge/` (gitignored):
  `index.json` (metadados) + `<id>.txt` (texto extraído).
- `add_knowledge_document` / `delete_knowledge_document` / índice; extração de PDF
  (PyMuPDF) e TXT/MD; resumo automático; limite de **15 MB**.
- `_build_user_knowledge_block(question, with_excerpts)`: **índice** (título +
  resumo de cada doc) sempre; **trechos relevantes** por palavras-chave da pergunta
  (docs < 8 mil caracteres entram inteiros; teto de ~12 mil caracteres injetados).
- Injeção: no **chat de texto** (`_ask_grok_with_context`, com trechos) e na **voz
  ao vivo** (`_kratos_voice_instructions`, só índice + resumos).
- Endpoints (JSON): `POST /api/kratos/knowledge` (upload base64),
  `GET /api/kratos/knowledge` (listar), `POST /api/kratos/knowledge/delete`
  (remover) — com aliases sob `/dashboard/...`.

### Frontend (`frontend/dashboard.html`)
- Botão **📎 Anexar conhecimento** na caixa do KRATOS + input de arquivo
  (PDF/TXT/MD). Upload via `FileReader` → base64 → POST.
- O KRATOS confirma no chat o que absorveu (nome, tamanho, resumo).
- Lista **📚 Conhecimento carregado** com tamanho e botão **Remover**.
- Validação de formato/tamanho no cliente; carga da lista na inicialização.

### Documentação
- Manual do usuário: item “📎 Anexar conhecimento”.
- `requirements.txt`: `pymupdf`. `.gitignore`: `data/users/*/knowledge/`.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK; `node --check`
  no `dashboard.html` → OK.
- Lógica: doc pequeno entra inteiro (recupera palavra-chave exclusiva); índice de
  voz correto; delete remove índice e arquivo.
- TestClient: upload TXT e **PDF** (texto extraído ok), limite de 15 MB recusado,
  formato inválido recusado, listar e remover.

## Limitações / evolução futura
- **DOCX** não suportado nesta fase (PDF/TXT/MD). Pode ser adicionado depois.
- Sem **busca semântica** (embeddings): a relevância é por palavras-chave —
  suficiente para o volume atual; evolução possível se a base crescer.

## Arquivos alterados
- `main.py` — módulo de conhecimento, injeção no chat e na voz, endpoints.
- `frontend/dashboard.html` — botão 📎, lista de conhecimento, manual.
- `requirements.txt`, `.gitignore`.
