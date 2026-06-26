# CONTEXTO — [NOME DO APP] (context pack do projeto)

Autor: Jossian Brito

> Modelo vindo do template **KRATOS Core**. Documento-semente para
> **reidratar o raciocínio do projeto** em qualquer momento (nova sessão de IA,
> novo desenvolvedor). Leia este arquivo + os ADRs em `docs/adr/` antes de começar.

> Atalho para a IA: "Leia `CLAUDE.md`, `docs/CONTEXTO.md`, os ADRs em
> `docs/adr/` e os relatórios em `docs/relatorios/` antes de começar."

## 1. O que é
[Descrição curta: o que o app faz e para quem.]

## 2. Stack e topologia
- **Backend:** FastAPI (ASGI) em `main.py`.
- **Frontend:** estático em `frontend/` (1 arquivo por página, JS inline +
  `kratos-core.js`).
- **Hospedagem:** [cPanel + Passenger + a2wsgi / outro]. Subcaminho via `root_path`.
- **Dados de runtime:** `data/` (gitignored).
- **Externos:** [APIs/integrações do domínio].

## 3. Decisões-chave (resumo — detalhes nos ADRs)
- **Acesso por convite (token)**, não login/senha; `ADMIN_TOKEN` chave-mestra;
  `ACCESS_CONTROL` desligado por padrão (kill-switch).
- **Subcaminho** exige tratar `root_path` em redirects/cookies.
- WSGI/Passenger **não faz WebSocket** → se precisar tempo real, use polling.
- [Outras decisões específicas do domínio → vire ADR.]

## 4. Convenções de trabalho (de `CLAUDE.md`)
1. Atualizar a documentação a cada mudança visível (mesmo commit).
2. Validar sintaxe antes do commit (`ast.parse` no `main.py`, `node --check` no JS).
3. Fluxo git: branch → commit → fast-forward de `main` → deploy puxa de `main`.
4. Relatório por etapa em `docs/relatorios/` (`AAAA-MM-DD-etapa-NN-<slug>.md`).
5. Autoria: `Autor: Jossian Brito` em todo `.md`.

## 5. O que está pronto
[Liste o que já foi implementado; comece pelo núcleo herdado do KRATOS Core.]

## 6. Pendências / próximas
[Backlog priorizado.]

## 7. Glossário do domínio
[Termos específicos.]

## 8. Genérico vs. específico
- **Genérico (herdado):** esqueleto FastAPI+estático, splash, acesso por convite,
  Central de Alertas, relatório PDF/DOCX, Voice Orb, suporte a subcaminho.
- **Específico (reescrever):** fonte de dados, regras de negócio, telas,
  conhecimento do assistente, identidade visual.
