# NPCP-RJ — Conhecimento estratégico (Portarias CPRJ nº 11 e nº 110/2026)

Autor: Jossian Brito

Base de conhecimento incorporada ao KRATOS (constante `KRATOS_NPCP_KNOWLEDGE` em
`main.py`, injetada no chat de texto e na voz ao vivo). Resume, com foco
estratégico para a SAAM (demanda de rebocador, janelas e restrições), as normas
locais vigentes da Capitania dos Portos do Rio de Janeiro.

**Fontes (anexadas):**
- Portaria CPRJ/COMOPNAV/MB nº 11, de 06/03/2026 — altera a NPCP-RJ (3ª Revisão),
  capítulos 4 (procedimentos para navios no porto / praticagem) e 5 (parâmetros
  operacionais). Em vigor desde 06/03/2026.
- Portaria nº 110/CPRJ/COMOPNAV/MB, de 14/05/2026 — altera a NPCP-RJ (3ª Revisão),
  capítulo 5 (Estaleiro EISA e Porto de Angra dos Reis/TPAR). Em vigor desde
  14/05/2026.

> Conhecimento de referência. Em decisão crítica, confirmar sempre na publicação
> oficial mais recente da CPRJ.

## Por que importa (foco SAAM)

Cada terminal define **quantos rebocadores** e **qual TTE mínimo** a manobra
exige — isso é demanda direta da nossa frota. Onde a norma **dispensa** rebocador
(tipicamente navios/EAM com Posicionamento Dinâmico — DP), a demanda cai. Janelas
de maré/vento e restrições diurno/noturno **concentram** manobras no tempo —
antecipam picos e sobreposição.

## Demanda de rebocador por área (oportunidades)

| Área | Exigência de rebocador | Condicionantes-chave |
|------|------------------------|----------------------|
| **Operação de ferro-gusa** (Cais Comercial, cabeços ~95–99 → Área de Fundeio nº 3; alt. nº 9) | **2 rebocadores**: 1 ≥ **45 TTE** (puxa a balsa) + 1 ≥ **25 TTE** (apoio atrac./desatrac.) | Comboio ~150 m (balsa LOA 108 m, boca 28 m, calado 4,9 m); 3 nós; sem praticagem obrigatória; visibilidade ≥ 2 MN, vento ≤ 20 nós; diurno/noturno. Aviso VHF 12. Recorrente. |
| **Porto de Angra dos Reis (TPAR)** — atracação longitudinal | **≥ 2 rebocadores azimutais de ≥ 45 TTE cada** | Navio-tipo até LOA 190 m; vento ≤ 15 nós (rajada 20), visib. ≥ 1 MN, maré de enchente 1:1 quando necessária; canal 1 navio/vez a 3 nós. EAM com DP **dispensa** rebocador. |
| **Estaleiro EISA** (Ilha do Governador) | **Reboque obrigatório** para cascos/embarcações (exceto pequeno porte) | Assessoria por **AMD**; transferência prático/AMD na isóbata de 10 m; vento ≤ 15 nós, velocidade < 5 nós; berços até LOA 230 m / boca 40 m. |

## Menos demanda (DP dispensa rebocador)

- **Terminal Brasco – Base Niterói:** navios-tipo com **DP dispensam rebocador**
  (atracação e desatracação); auxiliares só a critério do comandante. Manobras
  **somente nos estofos de maré**; vento < 15 nós, visib. > 2 MN, diurno/noturno;
  1 navio por vez no canal. POB: atracação a partir de 2 h antes da PM/BM;
  desatracação a partir de 1 h antes. Berços: B1 LOA 97 m, B2 LOA 45 m, B3 LOA 94 m.

## Outros navios-tipo

- **Subsea7:** LOA 85,5 m / boca 18,3 m / calado 3,04 m (3,46 m com maré 1:1).
- **Rio Brasil Terminal (RBT):** tipo 1 (EAM) LOA 160 m / boca 33 m; tipo 2
  (carga geral) LOA 140 m / boca 22 m; calado 5,7 m (até 6,5 m com maré 1:1).

## Canais, calados e restrições de porte (Porto do Rio)

- **Cais Comercial** por trecho de cabeços: 36–110 → 10,30 m (+0,70 maré, máx 11,00);
  110–129 → 9,00 m (máx 9,70); 129–205 → 8,50 m (máx 9,00) e **LOA ≤ 185 m**;
  205–216 → 8,20 m (máx 9,00).
- **TECON-RJ:** até **349 m de LOA**, calado até 14,50 m (15,30 m com maré).
  Prioridade do canal: porta-contêineres do próprio TECON e Ro-Ro. Programação
  prévia obrigatória; avisar Praticagem (VHF 12, "Praticagem Rio") com 30 min.
- **Restrição de porte trecho 197–216 (via TECON):** LOA 120–150 m sem restrição
  (diurno/noturno); LOA 150–185 m **apenas diurno**; acima de 185 m não passa.
  Navios-tanque do Terminal de Óleo (cabeços 197–205): regras específicas de canal
  por calado e bordo de atracação.

> **Implicação tática:** a restrição diurno-only para navios grandes concentra
> manobras de dia — antecipar pico e sobreposição no período diurno, com mais
> rebocadores demandados.

## Praticagem (ZP-15) — disponibilidade

- ERU: mínimo **58 fainas/quadrimestre** por prático (50% = 29; 75% = 43).
- Cota por subzona: Baía de Guanabara 14, Forno 1, Sepetiba/Ilha Grande/Angra 8,
  Açu 2 (total 25; as 33 restantes em qualquer subzona).
- Período de escala do prático: das **11h01** de um dia às **11h** do dia seguinte.

## Manutenção

Ao receber novas portarias/alterações da NPCP-RJ, atualizar **(1)** a constante
`KRATOS_NPCP_KNOWLEDGE` em `main.py` e **(2)** este documento, mantendo as datas
de vigência. Validar com `python3 -c "import ast; ast.parse(open('main.py').read())"`.
