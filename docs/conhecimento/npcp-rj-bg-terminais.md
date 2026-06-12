# NPCP-RJ — Terminais da Baía de Guanabara (fichas operacionais)

Autor: Jossian Brito

Fichas por terminal da **Baía de Guanabara** compiladas da NPCP-RJ (3ª Revisão,
Mod.2) + Portarias CPRJ nº 11 e nº 110/2026. É a base do foco atual do KRATOS
(`KRATOS_NPCP_KNOWLEDGE` em `main.py`). Dado central: **exigência de rebocadores
(quantidade, tipo, TTE)** por terminal e porte.

Fonte integral: `fontes/npcp-rj-3rev-mod2-extraido.md`. Em decisão crítica,
confirmar na publicação oficial.

## Cais da Gamboa (Cais Comercial)
- **Rebocadores:** LOA ≤ 165 m e calado ≤ 8 m → 2 TKM ≥ 43 TTE · LOA 165–200 m com giro → 2 (1 azimutal + 1 TKM) ou 3 TKM ≥ 43 TTE (sem giro: 2 TKM) · LOA > 200 m ou calado > 8 m → 2 azimutais ≥ 43 TTE.
- **Janela:** vento ≤ 20 nós; visib. ≥ 2 MN. Giro leve recomendado (carregar: atracar BE; descarregar: BB).
- **Restrições:** 1 navio por vez entre cabeços 205–237 durante operações de navio-tanque.

## Cais de São Cristóvão (Cais Comercial)
- **Rebocadores:** LOA ≤ 120 m (diurno/noturno) → 2 ≥ 40 TTE · 120–150 m → 3 ≥ 40 TTE (2 com bow thruster) · 150–185 m (**só diurno**) → 3 ≥ 40 TTE sendo 2 azimutais (2 azimutais com thruster; até 185 m exige cabeços 150–178 livres de boca > 30 m).
- **Calados por trecho:** 36–110 → 10,30 m (máx 11,00 c/ maré); 110–129 → 9,00 (máx 9,70); 129–205 → 8,50 (máx 9,00; LOA ≤ 185 m); 205–216 → 8,20 (máx 9,00).

## TECON-RJ
- **Porte:** até 349 m LOA / 52 m boca; calado 14,50 m (15,30 c/ maré).
- **Escada de reboque (calado ≤ 13 m):**
  | Porte | Rebocadores |
  |---|---|
  | LOA ≤ 155 m | 2, somatório 80 TTE (≥ 1 azimutal, mín 40/un.) |
  | 155–200 m | 2 azimutais, somatório 80 TTE |
  | 200–250 m (DWT 40–60k) | 3, somatório 90 TTE (2 azimutais); c/ thruster: 2 azimutais, 80 TTE |
  | 250–290 m (DWT 60–80k) | 3, somatório 140 TTE; c/ thruster: 120 TTE |
  | > 290 m sem thruster | 4, somatório 160 TTE (2 azimutais + 2 TKM); c/ thruster: 3, 140 TTE |
  | 295–335 m (boca 42–48,5), calado 14,5–14,6 m | 2 × 60 + 2 × 55 TTE, todos azimutais |
  | 335–349 m (boca 48,5–52), calado 14,5–14,6 m | 2 × 70 + 2 × 60 TTE, todos azimutais |
- **Janela/restrições:** 2 práticos quando LOA > 295 m ou boca > 42 m; vento ≤ 15 nós (≤ 10 na saída de ré dolfim–cabeço 277); corrente ≤ 0,6 nó; diurnas para os muito grandes. Programação prévia + aviso à Praticagem (VHF 12) com 30 min. Trecho 197–216: LOA 120–150 m diurno/noturno; 150–185 m só diurno; > 185 m não passa.

## Terminal de Óleo (cabeços 197–205)
- **Rebocadores:** navios-tanque LOA ≤ 185 m → **3 ≥ 45 TTE (2 azimutais + 1 TKM multi-eixo)**.
- **Canal por calado/bordo:** entrada calado 6,10–7,80 m só via canal TECON; saída atracado BE via Comercial (≤ 6,10 m); atracado BB sai via TECON (até 7,10 m, de ré com giro na bacia).

## Terminal Almirante Tamandaré (Ilha d'Água, Petrobras — PP-I/PP-II/PS-I/PS-II)
- Canal de 10 MN dragado a 17 m. **Todos os rebocadores azimutais ≥ 50 TTE.**
  | Píer | Navio-tipo | Rebocadores |
  |---|---|---|
  | PP-I | LOA 279,5 m / calado 15,85 m | DWT ≤ 60k e calado ≤ 12 m → 2; calado > 12 m → 3; DWT > 60k → 4 |
  | PP-II | LOA 259 m / calado 12–12,8 m | 3 (DWT ≤ 60k, calado ≤ 12 m) a 4 (DWT 60–135k ou calado > 12 m; 90–135k diurno) |
  | PS-I | LOA 186,4 m / calado 12 m | 2–3 conforme giro |
  | PS-II | LOA 175 m / calado 8,5 m | DWT ≤ 7k → 2; 7–15k → 3; > 15k → 4 |
- **Janela:** calado > 11,50 m vindo de fora da BG → entrada/saída **diurnas**; vento ≤ 20 nós (PS-II diurno ≤ 10 nós).

## GLP — TAIC / TAIR (Ilhas Comprida e Redonda, Petrobras)
- **TAIC:** 3 azimutais ≥ 45 TTE (calado leve ≤ 6,40 m) ou **4 azimutais ≥ 45 TTE** (carregado até 10,60 m). Atracação diurna; vento ≤ 20 nós; corrente ≤ 0,8 nó.
- **TAIR:** mínimo 3 azimutais ≥ 45 TTE; atracação **só diurna e contra a corrente**; desatracação BE noturna exige estofo e vento ≤ 10 nós.
- **Escolta:** rebocadores escoltam o navio desde antes da Ponte Rio-Niterói até o terminal (entrada) e até a Ponte (saída).

## GNL — Terminal Flexível de Regaseificação (PG-1/PG-2)
- **Navio-tipo:** LNGC até LOA 315 m / boca 51 m.
- **Rebocadores:** entrada → 2 (azimutais ou TKM), somatório ≥ 120 TTE, **cabos passados no vão central da Ponte**; atracação/desatracação/saída → 3 azimutais ≥ 40 TTE; **prontidão 24 h de 1 rebocador ≥ 45 TTE** com navio atracado.
- **Janela:** entrada só diurna; zona de segurança 500–600 m; trânsito interno ≤ 8 nós; VHF 13; documentação com 72 h úteis.

## Manguinhos (quadro de boias)
- **Navio-tipo:** LOA ~190 m / calado 11,47 m.
- **Rebocadores:** amarração → **4 ≥ 45 TTE (3 azimutais + 1 TKM)**; desamarração → 4 (2 azimutais + 2 TKM); **standby de 2 ≥ 45 TTE prontos em 15 min** enquanto amarrado.
- **Janela:** diurno; maré vazante obrigatória; vento ≤ 16 nós; sem trânsito paralelo Comercial/TECON durante operações.

## Neolubes (Ponte do Thun, Shell)
- **Navio-tipo:** LOA até 206 m / boca 32,5 m.
- **Rebocadores:** **2 azimutais ≥ 50 TTE em todas as manobras.**
- **Janela:** só diurno; 1 navio por vez; vento ≤ 15 nós; visib. ≥ 1 MN.

## Niterói / Caju — dispensas e casos leves
- **Brasco Base Niterói:** DP dispensa rebocador; manobras **só nos estofos**; 1 navio/vez. Berços: B1 97 m, B2 45 m, B3 94 m.
- **Brasco Rio (Caju):** 5 berços LOA 93,9 m; sem exigência explícita de rebocador.
- **MacLaren Ilha da Conceição / BHGE Caximbau:** tipo 1 (LOA 146 m) → 2 ≥ 40 TTE (azimutal/TKM/ASD); tipo 2 (LOA 97 m) com sistemas plenos → dispensado. Tipo 1 diurno, vento ≤ 12 nós, corrente ≤ 0,5 nó (enchente) / 0,2 (vazante).
- **MacLaren Ponta d'Areia:** berço D LOA 98 m; sem exigência explícita; corrente ≤ 1 nó, vento ≤ 15 nós.
- **Braskem:** LOA 130 m → 2 TKM ≥ 35 TTE; diurno; escolta da Ponte ao terminal.
- **Subsea7:** LOA 85,5 m → dispensado com sistemas plenos.
- **RBT/CLIP (Caju):** tipo 1 EAM (160 m) → dispensado; tipo 2 carga geral (140 m) → 2 TKM/ASD ≥ 45 TTE.

## Estaleiros
- **EISA (Ilha do Governador):** entrada/saída de cascos **sob reboque obrigatório** — DWT ≤ 45k → 2 azimutais; 45–55k → 3 azimutais; apoio marítimo com DP → dispensado. Assessoria por AMD; transferência prático/AMD na isóbata de 10 m. Berços até LOA 230 m.
- **Mauá (Niterói):** berços até LOA 230 m / boca 40 m; sem exigência explícita de rebocador na norma.

## Ferro-gusa (Cais Comercial ↔ Área de Fundeio nº 3, alt. nº 9)
- Comboio ~150 m (balsa 108 × 28 m): **1 rebocador ≥ 45 TTE + 1 ≥ 25 TTE**; 3 nós; sem praticagem obrigatória; visib. ≥ 2 MN, vento ≤ 20 nós; diurno/noturno; VHF 12. **Recorrente.**

## Regras gerais (BG)
- **Carga perigosa:** DWT ≥ 40.000 t → 2 rebocadores (TKM/ASD) ≥ 60 TTE com cabos passados; DWT 5.000–40.000 t → 2 ≥ 45 TTE.
- Rebocador/bow thruster obrigatório **não pode ser dispensado** pelo Comandante.
- Praticagem obrigatória para AB ≥ 500 (Lei 9.537/97); práticos nos PEP.
- Áreas de Fundeio numeradas (nº 2, 3, 9…) para espera/staging.
- VHF: Praticagem 12 ("Praticagem Rio"); 16 chamada/segurança; GNL 13.

## Leitura tática (SAAM-BGRA)
1. **Demanda pesada e recorrente:** TECON grandes (3–4 rebocadores, até 70 TTE),
   Tamandaré (azimutais ≥ 50 TTE, até 4), GLP TAIC/TAIR (3–4 azimutais ≥ 45 + escolta),
   GNL (cabos na Ponte + prontidão 24 h), Manguinhos (4 + standby), ferro-gusa.
2. **Demanda nula/baixa:** Brasco (DP), Subsea7, RBT tipo 1 — não dimensionar frota por elas.
3. **Concentração diurna:** Tamandaré (calado > 11,5 m), TAIR, GNL, Neolubes, Braskem,
   São Cristóvão > 150 m, TECON gigantes — picos de demanda de dia; planejar alocação.
4. **Prontidões/standby** (Manguinhos 15 min; GNL 24 h) são receita de disponibilidade
   além da manobra em si.

## Manutenção
Novas portarias: atualizar `KRATOS_NPCP_KNOWLEDGE` (main.py), estas fichas e o
resumo geral. Validar com `python3 -c "import ast; ast.parse(open('main.py').read())"`.
