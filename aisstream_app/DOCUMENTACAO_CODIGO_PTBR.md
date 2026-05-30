# Documentacao do Codigo - Guia Oficial (PT-BR)

Este documento define o padrao de documentacao recomendado para o projeto `aisstream_app`, com foco em clareza tecnica, manutencao e operacao em producao.

## Matriz de Documentacao

| Categoria | Tipo Especifico | Proposito Principal | Exemplos Praticos | Nivel de Detalhe Recomendado |
|---|---|---|---|---|
| Documentacao de Requisitos | Requisitos Funcionais | O que o sistema deve fazer | User Stories, Use Cases, User Story Map | Alto (must-have) |
| Documentacao de Requisitos | Requisitos Nao-Funcionais | Qualidade (performance, seguranca, usabilidade) | NFRs, SLAs, matriz de qualidade | Medio-Alto |
| Documentacao Tecnica / Arquitetura | Documento de Arquitetura (ADR) | Decisoes de design e trade-offs | Architecture Decision Records (ADR) | Alto |
| Documentacao Tecnica / Arquitetura | Diagrama de Arquitetura | Visao de alto nivel | C4 Model, UML, Draw.io, Mermaid | Alto |
| Documentacao Tecnica / Arquitetura | Especificacao de API | Contrato entre sistemas | OpenAPI/Swagger, AsyncAPI, RAML | Alto (obrigatorio para APIs) |
| Documentacao Tecnica / Arquitetura | Documentacao de Banco de Dados | Schema, queries, migracoes | ER Diagram, Data Dictionary | Medio |
| Documentacao de Codigo | README.md + Wiki interna | Como rodar o projeto localmente | Conventional README (GitHub) | Alto |
| Documentacao de Codigo | Comentarios no codigo + Docstrings | Explicar "por que" (nao o que) | JSDoc, Sphinx, Godoc, Doxygen | Medio (evite excesso) |
| Documentacao de Codigo | Changelog / Release Notes | O que mudou em cada versao | Keep a Changelog | Alto |
| Documentacao de Usuario (End-User) | Manual do Usuario / Help Center | Como usar o produto | Notion, Confluence, Zendesk, GitBook | Alto para produtos B2C/B2B |
| Documentacao de Usuario (End-User) | Tutoriais e Guias Rapidos | Passo a passo visual | Videos (Loom), screenshots | Medio-Alto |
| Documentacao de Usuario (End-User) | FAQ e Troubleshooting | Problemas comuns | Base de conhecimento do suporte | Medio |
| Documentacao de Operacao e Manutencao | Runbooks / Playbooks | Como operar em producao | Incident Response, Deployment Runbook | Alto (SRE/DevOps) |
| Documentacao de Operacao e Manutencao | Documentacao de Infraestrutura | Terraform, Docker, Kubernetes | IaC docs + diagramas | Alto |
| Documentacao de Operacao e Manutencao | Matriz de Responsabilidades (RACI) | Quem faz o que | RACI Matrix | Medio |
| Documentacao de Testes e Qualidade | Plano de Testes | Estrategia de testes | Test Plan (IEEE 829) | Medio |
| Documentacao de Testes e Qualidade | Relatorios de Testes | Resultados e cobertura | Test Coverage Report, Bug Tracker | Medio |
| Documentacao de Governanca e Compliance | Politica de Seguranca | Regras de seguranca | Security Policy, Threat Model | Alto (empresas grandes) |
| Documentacao de Governanca e Compliance | Licencas e Dependencias | Open-source e licencas | SBOM (Software Bill of Materials) | Alto (regulamentado) |
| Documentacao de Governanca e Compliance | Glossario e Termos | Vocabulario do dominio | Domain Glossary | Medio |

## Aplicacao Pratica no `aisstream_app`

### 1) Ja existente no projeto
- `README.md`: base de instalacao, execucao local e endpoints principais.
- `DEPLOY_CPANEL.md`: runbook operacional para deploy via cPanel.
- Comentarios no codigo (`main.py` e frontend): suporte tecnico pontual.

### 2) Recomendado criar em seguida (prioridade)
1. `docs/adr/` com ADRs das decisoes criticas:
   - WebSocket + fallback para polling.
   - Geofence persistente da Baia de Guanabara Interno.
   - Estrategia de atualizacao de trilhas e performance.
2. `docs/api/openapi.yaml`:
   - Contrato oficial dos endpoints REST e payloads.
3. `CHANGELOG.md`:
   - Registro de mudancas por versao, com impacto funcional/operacional.
4. `docs/runbooks/operacao-producao.md`:
   - Procedimentos de incidente (WS indisponivel, fallback, deploy bloqueado).
5. `docs/faq.md`:
   - Erros recorrentes (ex.: cPanel deploy bloqueado, SSL 525, WebSocket fail).

### 3) Estrutura sugerida de pastas

```text
docs/
  adr/
  api/
    openapi.yaml
  arquitetura/
  banco/
  runbooks/
  testes/
  usuario/
  governanca/
CHANGELOG.md
```

### 4) Padrao minimo por tipo de documento
- Requisitos: contexto, escopo, criterios de aceite, fora de escopo.
- ADR: problema, opcoes avaliadas, decisao, consequencias.
- API: endpoint, auth, request, response, erros e exemplos reais.
- Runbook: gatilho, diagnostico, acao, rollback, validacao final.
- FAQ: sintoma, causa provavel, acao recomendada.

### 5) Frequencia de atualizacao recomendada
- README/API/Runbooks: a cada mudanca funcional ou operacional relevante.
- Changelog: a cada release.
- ADR: sempre que houver decisao arquitetural com trade-off.
- FAQ: sempre que surgir incidente repetitivo.

