# Starter — novo aplicativo (reaproveitando a fundação KRATOS)

Autor: Jossian Brito

Guia + modelos para abrir um **novo repositório** sem perder o raciocínio. Copie os
modelos abaixo para o novo repo e ajuste o domínio.

## Passo a passo
1. **Criar repo** (idealmente a partir de um *template* do "KRATOS Core" — ver
   `docs/adr/0007-estrategia-de-reuso-multi-repo.md`).
2. Copiar para o novo repo, já no 1º commit:
   - `CLAUDE.md` (modelo abaixo)
   - `docs/CONTEXTO.md` (use o do KRATOS como base, troque o domínio)
   - `docs/adr/README.md` (mesmo template de ADR)
   - `docs/relatorios/` (manter a convenção `AAAA-MM-DD-etapa-NN-<slug>.md`)
3. Reaproveitar o **genérico**; reescrever o **específico** (checklist na seção final).
4. Ao iniciar uma sessão de IA: *"Leia CLAUDE.md, docs/CONTEXTO.md e os ADRs antes de começar."*

---

## Modelo de `CLAUDE.md` (preencher os [colchetes])

```md
# [NOME DO APP] — [subtítulo curto]

[1–2 linhas: o que é e para quem.] Hospedado em [host], deploy via [git pull/...].

## Estrutura (flat)
- `main.py` — backend FastAPI.
- `frontend/index.html` — [tela principal].
- `docs/` — CONTEXTO, ADRs, relatórios, propostas.

## Convenções importantes (sempre seguir)
1. Atualizar o manual/documentação a cada mudança visível, no mesmo commit.
2. Validar sintaxe antes de commitar:
   `python3 -c "import ast; ast.parse(open('main.py').read())"` e `node --check`
   no script do HTML alterado.
3. Fluxo git: branch de trabalho → commit → fast-forward de `main` → deploy puxa de `main`.
4. Relatório a cada fim de etapa em `docs/relatorios/` (`AAAA-MM-DD-etapa-NN-<slug>.md`).
5. Autoria: `Autor: Jossian Brito` em todo documento `.md`.

## Glossário do domínio
[termos específicos do novo app]

## Deploy
[comando de deploy]
```

---

## O que é GENÉRICO (reusar do KRATOS)
- Esqueleto **FastAPI + páginas estáticas** (1 arquivo por página, JS inline).
- **Splash screen** com progresso + botão de versão (`/versao`).
- **Acesso por convite (token)**: middleware de gate, `/entrar`, painel de convites
  no admin, `ACCESS_CONTROL` como kill-switch, `ADMIN_TOKEN` chave-mestra. (ADR 0004)
- **Central de Alertas**: som por gravidade (Web Audio), popup, notificação,
  preferências por tipo.
- **Geração de relatório PDF/DOCX** (reportlab + python-docx) + compartilhamento
  (Web Share API).
- **Dynamic Voice Orb** + integração de voz ao vivo (se houver assistente).
- **Padrões de robustez**: tratar `root_path`/subcaminho (ADR 0003); inicializar a
  UI essencial fora da cadeia de dados; redirect ao login em 401 no polling.
- **Convenções de contexto**: `CLAUDE.md`, `docs/CONTEXTO.md`, ADRs, relatórios.

## O que é ESPECÍFICO (reescrever por app)
- Fonte de dados do domínio (no KRATOS: AISStream).
- Geofences/áreas, normas, eventos e regras de negócio.
- Conhecimento do assistente (constantes de prompt do domínio).
- Identidade visual e textos.

## Regra de ouro para não perder o raciocínio
Toda decisão com trade-off vira **ADR**; todo fim de etapa vira **relatório**; o
"mapa mental" do projeto fica no **`docs/CONTEXTO.md`**. Assim, qualquer pessoa (ou
IA) reconstrói o porquê em minutos.
