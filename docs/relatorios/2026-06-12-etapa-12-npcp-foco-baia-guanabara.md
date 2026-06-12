# Etapa 12 — NPCP-RJ com foco na Baía de Guanabara (terminal a terminal)

Autor: Jossian Brito

Data: 2026-06-12

## Objetivo

Por decisão do usuário, focar o conhecimento normativo do KRATOS **exclusivamente
na Baía de Guanabara** (área de atuação da SAAM-BGRA), detalhando terminal a
terminal a exigência de rebocadores, e comprimindo as demais subzonas da ZP-15
(Itaguaí/Sepetiba, Angra/TPAR, Açu, Paraty, Forno) a uma linha de contexto.

## Método

Varredura dirigida do texto integral da NPCP-RJ
(`docs/conhecimento/fontes/npcp-rj-3rev-mod2-extraido.md`, ~502 mil caracteres)
por agente de exploração, compilando fichas por terminal da BG: navio-tipo,
exigência de rebocadores (quantidade/tipo/TTE), janelas e restrições.

## O que foi implementado

### Backend (`main.py`)
- `KRATOS_NPCP_KNOWLEDGE` **reescrita com foco BG** (~7,2 mil caracteres),
  agora em formato de bloco único legível (triple-quoted) com:
  - Cais Comercial (Gamboa/São Cristóvão) com escada por LOA e calados por trecho;
  - **TECON-RJ**: escada completa de reboque (somatórios de TTE de 80 a 160;
    gigantes 295–349 m = 4 azimutais de 55–70 TTE; 2 práticos; diurno);
  - **Terminal Almirante Tamandaré** (Ilha d'Água): azimutais ≥ 50 TTE, 2 a 4
    conforme píer/DWT/calado;
  - **GLP TAIC/TAIR**: 3–4 azimutais ≥ 45 TTE + escolta desde a Ponte;
  - **GNL**: cabos passados no vão da Ponte (somatório ≥ 120 TTE) + prontidão 24 h;
  - **Manguinhos**: 4 rebocadores ≥ 45 TTE + standby de 2 em 15 min;
  - **Neolubes**: 2 azimutais ≥ 50 TTE, só diurno;
  - Niterói/Caju (dispensas DP: Brasco, Subsea7, RBT; casos leves: MacLaren,
    BHGE, Braskem);
  - estaleiros (EISA com reboque obrigatório por DWT; Mauá), ferro-gusa,
    carga perigosa, regras de ouro, fundeadouros e VHF.
- Mantida a injeção nos dois caminhos (chat de texto + voz ao vivo).

### Documentação
- `docs/conhecimento/npcp-rj-bg-terminais.md` (novo): fichas completas por
  terminal da BG, com tabelas (TECON, Tamandaré) e leitura tática SAAM
  (onde a demanda é pesada/recorrente, onde é nula, onde concentra de dia,
  standby como receita de disponibilidade).
- `docs/KRATOS_CONHECIMENTO.md`: linha #18 atualizada (foco BG).
- `frontend/dashboard.html`: Manual do usuário atualizado com o foco BG e
  novos exemplos de pergunta.

## Validações
- `python3 -c "import ast; ast.parse(open('main.py').read())"` → OK.
- Bloco ~7,2k chars; 2 injeções (texto + voz).

## Lições aprendidas
- Varredura por agente sobre o texto-fonte integral permitiu recuperar exigências
  numéricas (TTE por píer/DWT) que a primeira destilação genérica não tinha — o
  recorte por área de atuação (BG) deixou o prompt menor e mais preciso ao mesmo
  tempo.

## Arquivos alterados
- `main.py` — `KRATOS_NPCP_KNOWLEDGE` reescrita (foco BG).
- `docs/conhecimento/npcp-rj-bg-terminais.md` (novo).
- `docs/KRATOS_CONHECIMENTO.md` — linha #18.
- `frontend/dashboard.html` — Manual do usuário.
