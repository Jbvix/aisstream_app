# NPCP-RJ (3ª Revisão) — Resumo estratégico para a SAAM

Autor: Jossian Brito

Síntese estratégica das **Normas e Procedimentos da Capitania dos Portos do Rio de
Janeiro** (NPCP-RJ, 3ª Revisão, Mod.2), com foco no que move a **demanda de
rebocadores** da SAAM: tração estática (TTE) exigida por porte/terminal, janelas,
calados e fundeadouros. Base incorporada ao KRATOS (`KRATOS_NPCP_KNOWLEDGE` em
`main.py`).

**Fontes:** `docs/conhecimento/fontes/npcp-rj-3rev-mod2-extraido.md` (texto integral
extraído) e as Portarias CPRJ nº 11/2026 e nº 110/2026
(`docs/conhecimento/npcp-rj-portarias-2026.md`).

> Documento de referência (texto OSTENSIVO). Em decisão crítica, confirmar sempre
> na publicação oficial mais recente.

## Estrutura da norma (6 capítulos)

1. Áreas de jurisdição — organização, jurisdição e limites (ZP-15).
2. Fatos e acidentes da navegação.
3. Dotação de material de segurança e documentos obrigatórios.
4. Procedimentos para navios no porto — tráfego, praticagem, rebocadores.
5. **Parâmetros operacionais** — calado máximo, terminais, berços, fundeadouros.
6. Vias navegáveis — navegabilidade, sinalização, canais.

## Jurisdição (ZP-15)

Baía de Guanabara (Porto do Rio e Niterói), Baía de Sepetiba (Porto de Itaguaí,
Porto Sudeste), Baía da Ilha Grande / Angra dos Reis (TPAR e terminais), Porto do
Açu, Paraty e Porto do Forno.

## Escada de reboque por porte (TTE) — a métrica de demanda

Regra geral do Porto do Rio (Cais Comercial / canais), salvo regra específica do
terminal. **TTE = tonelada de tração estática** (bollard pull).

| Porte do navio | Rebocadores exigidos |
|----------------|----------------------|
| LOA ≤ 120 m (diurno/noturno) | 2 rebocadores ≥ 40 TTE |
| LOA 120–150 m | 3 rebocadores ≥ 40 TTE (2 se tiver bow thruster) |
| LOA ≤ 165–185 m (diurnas) | 3 rebocadores ≥ 40 TTE, sendo 2 azimutais (2 azimutais se thruster); restrição se houver navio de boca > 30 m entre cabeços 150–178 |
| LOA > 200 m **ou** calado > 8 m | 2 rebocadores azimutais ≥ 43 TTE |
| Navio-tanque Terminal de Óleo, LOA ≤ 185 m | 3 rebocadores ≥ 45 TTE (2 azimutais + 1 TKM multi-eixo) |
| TECON-RJ 295–335 m LOA (ou boca 42–48,5 m) | 2 × 60 TTE + 2 × 55 TTE, todos azimutais |
| TECON-RJ 335–349 m LOA (ou boca 48,5–52 m) | 2 × 70 TTE + 2 × 60 TTE, todos azimutais |
| LOA > 290 m sem thruster | 4 rebocadores, somatório 160 TTE (≥ 2 azimutais + 2 TKM, mín. 40/un.) |
| LOA > 290 m com thruster | 3 rebocadores, somatório 140 TTE |

## Terminais e casos de alta demanda

- **Navio de gás (LNGC):** 5 rebocadores azimutais — 2 × ≥ 70 TTE + 3 × ≥ 60 TTE.
- **Píeres de petróleo (PP-I, PP-II, PS-I, PS-II):** rebocadores azimutais ≥ 50 TTE.
- **Quadro de boias:** 2 rebocadores ≥ 45 TTE disponíveis para atendimento em 15 min
  enquanto o navio está no quadro; amarração com 4 rebocadores de 45 TTE (3 azimutais
  + 1 TKM); desamarração 2 azimutais + 2 TKM.
- **Carga perigosa:** DWT ≥ 40.000 t → 2 rebocadores ≥ 60 TTE com cabos passados;
  5.000 < DWT < 40.000 t → 2 rebocadores ≥ 45 TTE.
- **Ferro-gusa (Cais Comercial):** comboio balsa + 1 reb. ≥ 45 TTE + 1 ≥ 25 TTE
  (ver doc das portarias).
- **Angra/TPAR:** ≥ 2 azimutais ≥ 45 TTE (longitudinal); DP dispensa.
- **Brasco-Niterói:** DP dispensa rebocador (só estofos de maré).

## Regras de ouro

- Quando o rebocador (e o bow thruster) é **obrigatório**, o Comandante **não pode
  dispensá-lo**.
- **Praticagem obrigatória** para embarcações com AB ≥ 500 (Lei nº 9.537/1997).
  Práticos aguardam nos **Pontos de Espera de Prático (PEP)** da ZP-15.

## Fundeadouros, velocidade e contato

- **Áreas de Fundeio** numeradas (ex.: nº 2, nº 3, nº 9) para espera/staging.
- **Velocidade:** 3 nós em canais restritos (Baía da Ilha Grande) e até 5 nós em
  áreas específicas.
- **VHF:** Praticagem canal 12 ("Praticagem Rio", via Atalaia); canal 16 para
  chamada/segurança.

## Implicações táticas (SAAM)

- O número e o TTE de rebocadores por manobra dependem diretamente de LOA/boca/calado
  do navio e do terminal — cruzar a programação (POB + características) com esta
  escada permite **dimensionar a demanda** turno a turno.
- Navios grandes (≥ 150–185 m) frequentemente só manobram **de dia** — concentração
  de demanda no período diurno.
- Terminais com **DP** (Brasco-Niterói, EAM em Angra) reduzem demanda — priorizar
  esforço comercial onde o reboque é obrigatório e pesado (gusa, TECON grandes,
  petróleo, gás, Angra longitudinal).

## Manutenção

Novas portarias/revisões: atualizar **(1)** `KRATOS_NPCP_KNOWLEDGE` em `main.py`,
**(2)** este resumo e **(3)** o texto-fonte em `fontes/`. Validar com
`python3 -c "import ast; ast.parse(open('main.py').read())"`.
