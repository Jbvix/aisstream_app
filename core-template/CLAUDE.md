# [NOME DO APP] — [subtítulo curto]

> Este `CLAUDE.md` veio do template **KRATOS Core**. Preencha os [colchetes]
> com o domínio do novo app e remova esta nota.

[1–2 linhas: o que é e para quem.] Hospedado em [host], deploy via [git pull/...].

## Estrutura (flat)
- `main.py` — backend FastAPI (acesso por convite, relatórios, health; genérico).
- `frontend/index.html` — [tela principal].
- `frontend/kratos-core.js` — helpers reutilizáveis (API, alertas, orb).
- `docs/` — CONTEXTO, ADRs, relatórios.

## O que é genérico (não reescrever sem motivo)
Acesso por convite, Central de Alertas, relatório PDF/DOCX, Voice Orb, splash,
suporte a subcaminho (`root_path`). Procure por `TODO-DOMINIO` para o que trocar.

## REGRAS DE TRABALHO (sempre seguir)
1. **Atualizar a documentação/manual a cada mudança visível**, no mesmo commit.
2. **Validar sintaxe antes de commitar:**
   `python3 -c "import ast; ast.parse(open('main.py').read())"` e `node --check`
   no script do HTML alterado.
3. Fluxo git: branch de trabalho → commit → fast-forward de `main` → deploy puxa de `main`.
4. **Relatório a cada fim de etapa** em `docs/relatorios/`
   (`AAAA-MM-DD-etapa-NN-<slug>.md`; não usar prefixo `RELATORIO_SESSAO_`).
5. **Autoria:** `Autor: Jossian Brito` (linha logo abaixo do título) em todo `.md`.

## Glossário do domínio
[termos específicos do novo app]

## Deploy
[comando de deploy — ex.: `cd ~/app && git pull origin main && touch tmp/restart.txt`]
