# KRATOS — Inteligência Naval Estratégica

App de monitoramento AIS do Porto do Rio de Janeiro / Baía de Guanabara, focado
em estratégia de market share e acompanhamento dos rebocadores concorrentes.
Hospedado em cPanel (`https://tuglife.live/aisstream/`), deploy via Git pull.

## Estrutura (flat)
- `main.py` — backend FastAPI (relay AIS, geofences, praticagem, market share, KRATOS/xAI).
- `frontend/index.html` — mapa Leaflet ao vivo.
- `frontend/dashboard.html` — painel estratégico (inclui o **Manual do usuário** no botão 📘).
- `praticagem_saa.py` — scraper da Praticagem-RJ.
- `docs/` — proposta, guia de deploy, etc.

## Convenções importantes
- **SAA = SAAM**: na programação da Praticagem (campo EMP.RB), o código `SAA`
  representa a SAAM (nossa empresa). `WIL` e `CAM` são concorrentes.
- Assistente estratégico chama-se **KRATOS**.
- Dados de runtime (`data/users/*/...`) são gitignored — não versionar.

## REGRAS DE TRABALHO (sempre seguir)
1. **Atualizar o manual a cada implementação.** Toda mudança que afete o uso
   ou comportamento visível do app deve ser refletida no Manual do usuário em
   `frontend/dashboard.html` (bloco `.manual-modal__body`), no mesmo commit.
2. Validar sintaxe antes de commitar: `python3 -c "import ast; ast.parse(open('main.py').read())"`
   para o backend e `node --check` no script do HTML alterado.
3. Após aprovação/feature pronta: commit na branch de trabalho, push, e
   fast-forward de `main` (produção puxa de `main`).

## Deploy (cPanel)
No servidor: `cd ~/aisstream_app && git pull origin main && touch tmp/restart.txt`
