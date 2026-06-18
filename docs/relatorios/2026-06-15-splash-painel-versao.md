# Botão na splash → Painel de Implementações da Versão (responsivo)

Autor: Jossian Brito

Data: 2026-06-15

## Objetivo
Adicionar, na splash screen, um botão de acesso ao **painel de implementações da
versão**, com responsividade.

## O que foi implementado
- **`frontend/versao.html`** (novo): página **responsiva** (grid `auto-fill
  minmax(300px,1fr)`; 1 coluna em ≤600px) com todas as implementações em cards por
  eixo (Núcleo & Mapa, Inteligência, Operação & Alertas, Mobilidade & UX, Segurança
  & Integrações), seção "Pendente" e link para baixar o painel em imagem.
- **Rota** `GET /versao` (e `/versao/`) servindo a página.
- **Imagem** `frontend/KRATOS_painel_implementacoes.png` (cópia servível pelo mount
  `/frontend`) para download/visualização.
- **Splash** (`index.html`): botão **"📋 Ver implementações da versão"** que abre
  `/versao` em nova aba; href montado por JS respeitando o subcaminho (ex.:
  `/aisstream/versao`). CSS responsivo (pílula, reduz em ≤480px, `max-width:90vw`).

## Validações
- `ast.parse(main.py)` e `node --check` (index.html, versao.html) → OK.
- TestClient: `GET /versao` → 200 (HTML com a grade); imagem em
  `/frontend/KRATOS_painel_implementacoes.png` → 200 image/png.

## Observação
- `/versao` segue a trava de acesso (ACCESS_CONTROL) como o resto do app; o usuário
  que vê a splash já está autenticado, então o botão abre normalmente.

## Arquivos alterados
- `frontend/versao.html` (novo) · `frontend/KRATOS_painel_implementacoes.png` (novo)
- `frontend/index.html` — botão + CSS na splash
- `main.py` — rota `/versao`
