# ADR 0007 - Estratégia de reúso entre repositórios (novo app)

## Status
Proposto

## Contexto
Novos aplicativos (marítimos ou não) compartilharão uma fundação comum, mas terão
domínio próprio. Precisamos reusar sem acoplar nem "perder o raciocínio".

## Opções consideradas
- A) Copiar/colar manual (divergência rápida).
- B) **Repo template** (GitHub "Template repository") com o "KRATOS Core".
- C) Pacote/lib Python compartilhada instalável.
- D) Monorepo / git submodule.

## Decisão
Começar por B (template), evoluindo para C quando a parte comum estabilizar.
"KRATOS Core" (genérico) = esqueleto FastAPI + páginas estáticas + splash + acesso
por convite + Central de Alertas + geração de relatório PDF/DOCX + Dynamic Voice Orb
+ convenções (CLAUDE.md, ADRs, relatórios). **Específico** (reescrever por app) =
geofences/normas/eventos do domínio, integrações de dados.

## Consequências
- (+) Novo app nasce com fundação testada e com as convenções de contexto.
- (+) Caminho claro para extrair uma lib quando valer a pena.
- (−) Template não recebe atualizações automáticas do core (diverge com o tempo) →
  por isso migrar para lib (C) quando o core amadurecer.

## Próximos passos
1. Marcar um repositório base como *template* no GitHub.
2. Isolar o genérico do específico (checklist no `docs/CONTEXTO.md`).
3. No novo repo: `CLAUDE.md` + `docs/CONTEXTO.md` próprios desde o 1º commit.

## Referências
`docs/CONTEXTO.md` (seção 8), `CLAUDE.md`.
