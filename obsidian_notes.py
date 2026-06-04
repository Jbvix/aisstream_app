"""
obsidian_notes.py — Motor de links & grafos (Sprint 2 da integração Obsidian).

Transforma o estado do KRATOS (manobras da Praticagem, posições AIS, geofences,
market share, maré/vento) num conjunto de **notas Markdown interligadas** que
formam um grafo no Obsidian:

    Manobra ↔ Navio ↔ Berço ↔ Rebocador ↔ Dia/Clima ↔ Empresa

Princípios:
- Módulo **puro**: não importa ``main``. Recebe os dados como argumentos, o que
  o torna testável isoladamente e evita import circular.
- **Links por basename:** o Obsidian resolve ``[[Nome]]`` pelo nome do arquivo
  (sem pasta). Por isso o nome de exibição de cada entidade é usado tanto como
  título/arquivo quanto como alvo de link — garantindo que as arestas fechem.
- **Tags estruturadas** seguindo a proposta (``#kratos/rebocador/saam`` etc.).
- Caminhos retornados são **relativos ao prefixo** (ex.: ``navios/X``); quem
  sobe (``obsidian_supabase.upload_note``) acrescenta o prefixo ``kratos/``.

Função principal:
    build_vault(overview, vessels, metocean, *, saam_fleet, competitor_tugs,
                now_iso) -> list[{"path", "markdown", "title"}]
"""

import re
import unicodedata
from collections import defaultdict

from obsidian_supabase import build_note


OWN_EMP = "SAA"  # EMP.RB "SAA" == SAAM (nossa empresa); WIL/CAM são concorrentes.

# Caracteres proibidos em nome de arquivo / problemáticos em links do Obsidian.
_ILLEGAL = re.compile(r'[\\/:*?"<>|#^\[\]]+')


def _fname(name: str) -> str:
    """Nome de exibição seguro para arquivo E para alvo de link ``[[...]]``."""
    text = (str(name) if name is not None else "").strip()
    text = _ILLEGAL.sub("-", text)
    text = re.sub(r"\s+", " ", text).strip(" -.")
    return text or "Sem nome"


def _link(name: str) -> str:
    return f"[[{_fname(name)}]]"


def _is_own(emp: str) -> bool:
    return (str(emp or "").strip().upper()) == OWN_EMP


def _emp_norm(emp: str) -> str:
    return (str(emp or "").strip().upper()) or "N/A"


def _date_of(iso: str) -> str:
    """Parte AAAA-MM-DD de um ISO; cai para string vazia se inválido."""
    s = str(iso or "").strip()
    return s[:10] if len(s) >= 10 and s[4] == "-" else ""


def _norm(text: str) -> str:
    """Minúsculas sem acentos, para comparar nomes de navios entre fontes."""
    t = unicodedata.normalize("NFD", str(text or "").strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _fmt(value, suffix: str = "") -> str:
    s = str(value).strip() if value is not None else ""
    if not s or s in {"—", "-"}:
        return "—"
    return f"{s}{suffix}"


def _wind_text(metocean: dict) -> str:
    spd = metocean.get("windSpeedKmh")
    deg = metocean.get("windDirectionDeg")
    if spd is None:
        return "—"
    try:
        rose = ["N", "NE", "L", "SE", "S", "SO", "O", "NO"]
        card = rose[int((float(deg) + 22.5) % 360 // 45)] if deg is not None else ""
    except Exception:
        card = ""
    txt = f"{round(float(spd))} km/h"
    return f"{txt} ({card})" if card else txt


# --- Geração das notas --------------------------------------------------------

def build_vault(overview: dict, vessels: list, metocean: dict, *,
                saam_fleet: list, competitor_tugs: dict, now_iso: str) -> list:
    """Constrói todas as notas interligadas. Retorna lista {path, markdown, title}."""
    overview = overview or {}
    vessels = vessels or []
    metocean = metocean or {}

    maneuvers = list(overview.get("saaManeuvers") or [])
    market = (overview.get("marketShare") or {}).get("rows") or []
    occupancy = overview.get("occupancy") or []

    # Índices auxiliares.
    vessel_by_norm = {}
    for v in vessels:
        vessel_by_norm.setdefault(_norm(v.get("shipName")), v)

    notes: list = []

    notes.extend(_maneuver_and_entity_notes(maneuvers, vessel_by_norm))
    notes.extend(_tug_notes(vessels, saam_fleet, competitor_tugs))
    notes.extend(_company_notes(market, maneuvers))
    notes.extend(_daily_notes(maneuvers, metocean, now_iso))
    notes.append(_index_note(maneuvers, vessels, market, now_iso))

    return notes


def _maneuver_and_entity_notes(maneuvers: list, vessel_by_norm: dict) -> list:
    """Notas de Manobra + agrega Navios e Berços (com backlinks)."""
    notes = []
    by_vessel = defaultdict(list)
    by_berth = defaultdict(list)

    for m in maneuvers:
        vessel = _fmt(m.get("vesselName"))
        berth = _fmt(m.get("berthName"))
        emp = _emp_norm(m.get("empRb"))
        day = _date_of(m.get("recordedAt"))
        status = _fmt(m.get("status"))
        title = f"{vessel} — {berth}" + (f" ({day})" if day else "")

        tags = ["kratos/manobra", "kratos/manobra/" + ("saam" if _is_own(emp) else "concorrente")]
        fm = {
            "tipo": "manobra",
            "navio": _fname(vessel),
            "berco": _fname(berth),
            "empresa": emp,
            "status": status,
            "pob": _fmt(m.get("pob")),
            "calado": _fmt(m.get("cal")),
            "loa": _fmt(m.get("loa")),
            "boca": _fmt(m.get("boca")),
            "dwt": _fmt(m.get("dwt")),
            "gt": _fmt(m.get("gt")),
            "fonte": _fmt(m.get("source")),
            "registrado_em": _fmt(m.get("recordedAt")),
        }
        links = [f"Navio:: {_link(vessel)}", f"Berço:: {_link(berth)}",
                 f"Empresa:: {_link(emp)}"]
        if day:
            links.append(f"Dia:: {_link(day)}")
        body = (
            f"Manobra de {_link(vessel)} em {_link(berth)} "
            f"({'SAAM' if _is_own(emp) else emp}).\n\n"
            "## Conexões\n" + "\n".join(f"- {l}" for l in links) + "\n\n"
            "## Dados\n"
            f"- **Status:** {status}\n"
            f"- **POB:** {_fmt(m.get('pob'))}\n"
            f"- **Calado:** {_fmt(m.get('cal'), ' m')}  |  **LOA:** {_fmt(m.get('loa'), ' m')}"
            f"  |  **Boca:** {_fmt(m.get('boca'), ' m')}\n"
            f"- **DWT:** {_fmt(m.get('dwt'))}  |  **GT:** {_fmt(m.get('gt'))}\n"
            f"- **Nota:** {_fmt(m.get('note'))}\n"
        )
        notes.append({
            "path": f"manobras/{_fname(title)}",
            "title": title,
            "markdown": build_note(title, body, frontmatter=fm, tags=tags),
        })
        by_vessel[vessel].append((title, berth, emp, status, day))
        if berth != "—":
            by_berth[berth].append((title, vessel, emp, status, day))

    notes.extend(_vessel_notes(by_vessel, vessel_by_norm))
    notes.extend(_berth_notes(by_berth))
    return notes


def _vessel_notes(by_vessel: dict, vessel_by_norm: dict) -> list:
    notes = []
    for vessel, items in by_vessel.items():
        if vessel == "—":
            continue
        live = vessel_by_norm.get(_norm(vessel))
        fm = {"tipo": "navio", "navio": _fname(vessel), "total_manobras": len(items)}
        lines = [f"Histórico de manobras de **{vessel}** ({len(items)}).", ""]
        if live:
            geos = ", ".join(_link(g) for g in (live.get("geofencesInside") or [])) or "—"
            fm["mmsi"] = str(live.get("mmsi") or "")
            fm["categoria"] = str(live.get("shipCategory") or "")
            lines += [
                "## Localização atual (AIS)",
                f"- **MMSI:** {live.get('mmsi') or '—'}  |  **Categoria:** {live.get('shipCategory') or '—'}",
                f"- **SOG:** {_fmt(round(float(live.get('sog') or 0), 1), ' kn')}"
                f"  |  **COG:** {_fmt(round(float(live.get('cog') or 0)), '°')}",
                f"- **Em geofence:** {geos}",
                "",
            ]
        lines.append("## Manobras")
        for title, berth, emp, status, day in items:
            tag = "SAAM" if _is_own(emp) else emp
            lines.append(f"- {_link(title)} — {_link(berth)} · {tag} · {status}"
                         + (f" · {_link(day)}" if day else ""))
        notes.append({
            "path": f"navios/{_fname(vessel)}",
            "title": vessel,
            "markdown": build_note(vessel, "\n".join(lines), frontmatter=fm,
                                   tags=["kratos/navio/comercial"]),
        })
    return notes


def _berth_notes(by_berth: dict) -> list:
    notes = []
    for berth, items in by_berth.items():
        fm = {"tipo": "berco", "berco": _fname(berth), "total_manobras": len(items)}
        lines = [f"Berço **{berth}** — {len(items)} manobra(s) registada(s).", "", "## Manobras"]
        for title, vessel, emp, status, day in items:
            tag = "SAAM" if _is_own(emp) else emp
            lines.append(f"- {_link(title)} — {_link(vessel)} · {tag} · {status}"
                         + (f" · {_link(day)}" if day else ""))
        notes.append({
            "path": f"bercos/{_fname(berth)}",
            "title": berth,
            "markdown": build_note(berth, "\n".join(lines), frontmatter=fm,
                                   tags=["kratos/berço"]),
        })
    return notes


def _tug_notes(vessels: list, saam_fleet: list, competitor_tugs: dict) -> list:
    """Notas de Rebocador (SAAM e concorrentes) com velocidade/rumo/base atual."""
    by_mmsi = {str(v.get("mmsi")): v for v in vessels if v.get("mmsi")}
    notes = []

    def tug_note(name, mmsi, company, own):
        live = by_mmsi.get(str(mmsi))
        scope = "saam" if own else "concorrente"
        fm = {"tipo": "rebocador", "empresa": company, "mmsi": str(mmsi or "")}
        lines = [f"Rebocador **{name}** — {'SAAM' if own else company}.", ""]
        if live:
            geos = (live.get("geofencesInside") or [])
            base_link = ", ".join(_link(g) for g in geos) or "—"
            fm["sog_kn"] = round(float(live.get("sog") or 0), 1)
            fm["cog_deg"] = round(float(live.get("cog") or 0))
            fm["em_base"] = bool(live.get("inRebocadorBase"))
            lines += [
                "## Situação atual (AIS)",
                f"- **Velocidade (SOG):** {round(float(live.get('sog') or 0), 1)} kn",
                f"- **Rumo (COG):** {round(float(live.get('cog') or 0))}°",
                f"- **Em base/geofence:** {base_link}",
                f"- **Na base de rebocador:** {'sim' if live.get('inRebocadorBase') else 'não'}",
            ]
        else:
            lines.append("_Sem posição AIS recente._")
        notes.append({
            "path": f"rebocadores/{_fname(name)}",
            "title": name,
            "markdown": build_note(name, "\n".join(lines), frontmatter=fm,
                                   tags=[f"kratos/rebocador/{scope}"]),
        })

    for tug in (saam_fleet or []):
        mmsi = str(tug.get("mmsi"))
        live = by_mmsi.get(mmsi)
        name = (live.get("shipName") if live else None) or tug.get("name") or f"SAAM {mmsi}"
        tug_note(name, mmsi, "SAAM", True)

    for company, tugs in (competitor_tugs or {}).items():
        for tug in tugs:
            mmsi = str(tug.get("mmsi"))
            live = by_mmsi.get(mmsi)
            name = (live.get("shipName") if live else None) or tug.get("name") or f"{company} {mmsi}"
            tug_note(name, mmsi, company, False)
    return notes


def _company_notes(market: list, maneuvers: list) -> list:
    """Notas de Empresa com market share e lista de manobras."""
    notes = []
    man_by_emp = defaultdict(list)
    for m in maneuvers:
        man_by_emp[_emp_norm(m.get("empRb"))].append(m)

    emps = {_emp_norm(r.get("empRb")) for r in market} | set(man_by_emp.keys())
    share_by_emp = {_emp_norm(r.get("empRb")): r for r in market}

    for emp in sorted(emps):
        if emp == "N/A":
            continue
        own = _is_own(emp)
        display = "SAAM (própria)" if own else f"{emp} (concorrente)"
        row = share_by_emp.get(emp, {})
        fm = {
            "tipo": "empresa", "codigo": emp,
            "manobras": row.get("count", len(man_by_emp.get(emp, []))),
            "share_pct": row.get("sharePct", 0),
            "propria": own,
        }
        lines = [
            f"**{display}** — código EMP.RB `{emp}`.", "",
            f"- **Manobras:** {fm['manobras']}",
            f"- **Market share:** {fm['share_pct']}%", "",
            "## Manobras",
        ]
        for m in man_by_emp.get(emp, []):
            v = _fmt(m.get("vesselName"))
            b = _fmt(m.get("berthName"))
            day = _date_of(m.get("recordedAt"))
            lines.append(f"- {_link(f'{v} — {b}' + (f' ({day})' if day else ''))}")
        notes.append({
            "path": f"empresas/{_fname(emp)}",
            "title": emp,
            "markdown": build_note(f"{emp} — {display}", "\n".join(lines), frontmatter=fm,
                                   tags=[f"kratos/empresa/{'saam' if own else 'concorrente'}"]),
        })
    return notes


def _daily_notes(maneuvers: list, metocean: dict, now_iso: str) -> list:
    """Condição Diária: vento + maré reais interligados com as manobras do dia."""
    by_day = defaultdict(list)
    for m in maneuvers:
        day = _date_of(m.get("recordedAt"))
        if day:
            by_day[day].append(m)
    if not by_day:
        today = _date_of(now_iso)
        if today:
            by_day[today] = []

    wind = _wind_text(metocean)
    tide = str(metocean.get("tide") or "—").strip() or "—"
    today = _date_of(now_iso)
    notes = []
    for day, items in by_day.items():
        fm = {"tipo": "dia", "data": day, "manobras": len(items)}
        lines = [f"## Condições — {day}", ""]
        if day == today:
            # Maré/vento são instantâneos: só fazem sentido na nota de hoje.
            fm["vento"] = wind
            fm["mare"] = tide
            lines += [
                f"- **Vento:** {wind}",
                f"- **Maré:** {tide}",
            ]
            if metocean.get("tideNextTurn"):
                lines.append(f"- **Próxima virada de maré:** {metocean.get('tideNextTurn')}")
            lines.append("")
        lines.append("## Manobras do dia")
        if items:
            for m in items:
                v = _fmt(m.get("vesselName"))
                b = _fmt(m.get("berthName"))
                emp = _emp_norm(m.get("empRb"))
                tag = "SAAM" if _is_own(emp) else emp
                lines.append(f"- {_link(f'{v} — {b} ({day})')} — {_link(b)} · {tag}")
        else:
            lines.append("_Sem manobras registadas._")
        notes.append({
            "path": f"dias/{_fname(day)}",
            "title": day,
            "markdown": build_note(day, "\n".join(lines), frontmatter=fm, tags=["kratos/dia"]),
        })
    return notes


def _index_note(maneuvers: list, vessels: list, market: list, now_iso: str) -> dict:
    own = next((r for r in market if _is_own(r.get("empRb"))), None)
    lines = [
        "Mapa de conteúdo (MOC) gerado pelo KRATOS. Use o **Graph View** "
        "(`Ctrl+G`) para visualizar as conexões.", "",
        "## Resumo",
        f"- **Manobras:** {len(maneuvers)}",
        f"- **Embarcações AIS ao vivo:** {len(vessels)}",
        f"- **Market share SAAM:** {own.get('sharePct') if own else 0}%", "",
        "## Pastas",
        "- `manobras/` · `navios/` · `bercos/` · `rebocadores/` · `empresas/` · `dias/`", "",
        "## Tags",
        "- `#kratos/manobra` · `#kratos/navio/comercial` · `#kratos/berço`",
        "- `#kratos/rebocador/saam` · `#kratos/rebocador/concorrente`",
        "- `#kratos/empresa/saam` · `#kratos/empresa/concorrente` · `#kratos/dia`",
    ]
    return {
        "path": "KRATOS",
        "title": "KRATOS — Índice",
        "markdown": build_note("KRATOS — Índice", "\n".join(lines),
                               frontmatter={"tipo": "indice"}, tags=["kratos/indice"]),
    }


# --- Grafo para visualização web (mesmo modelo das notas) ---------------------

def build_graph(overview: dict, vessels: list, *, saam_fleet: list,
                competitor_tugs: dict) -> dict:
    """Monta nós e arestas do grafo KRATOS para render no navegador.

    Reaproveita o mesmo modelo das notas (Manobra ↔ Navio ↔ Berço ↔ Empresa ↔
    Dia, e Rebocador ↔ Empresa). Retorna ``{"nodes": [...], "links": [...]}``
    com ``group`` por tipo (para colorir igual ao Graph View do Obsidian).
    """
    overview = overview or {}
    vessels = vessels or []
    maneuvers = list(overview.get("saaManeuvers") or [])

    nodes: dict = {}
    links: list = []

    def add_node(nid: str, label: str, group: str):
        if nid and nid not in nodes:
            nodes[nid] = {"id": nid, "label": label, "group": group}

    def add_link(a: str, b: str):
        if a and b and a != b:
            links.append({"source": a, "target": b})

    for m in maneuvers:
        vessel = _fmt(m.get("vesselName"))
        berth = _fmt(m.get("berthName"))
        emp = _emp_norm(m.get("empRb"))
        day = _date_of(m.get("recordedAt"))
        title = f"{vessel} — {berth}" + (f" ({day})" if day else "")
        man_id = _fname(title)
        add_node(man_id, title, "manobra")
        if vessel != "—":
            vid = _fname(vessel)
            add_node(vid, vessel, "navio")
            add_link(man_id, vid)
        if berth != "—":
            bid = _fname(berth)
            add_node(bid, berth, "berco")
            add_link(man_id, bid)
        if emp != "N/A":
            eid = _fname(emp)
            own = _is_own(emp)
            add_node(eid, "SAAM" if own else emp,
                     "empresa-saam" if own else "empresa-concorrente")
            add_link(man_id, eid)
        if day:
            did = _fname(day)
            add_node(did, day, "dia")
            add_link(man_id, did)

    by_mmsi = {str(v.get("mmsi")): v for v in vessels if v.get("mmsi")}

    def add_tug(name: str, company: str, own: bool):
        tid = _fname(name)
        add_node(tid, name, "rebocador-saam" if own else "rebocador-concorrente")
        eid = _fname(company)
        add_node(eid, "SAAM" if own else company,
                 "empresa-saam" if own else "empresa-concorrente")
        add_link(tid, eid)

    for tug in (saam_fleet or []):
        mmsi = str(tug.get("mmsi"))
        live = by_mmsi.get(mmsi)
        name = (live.get("shipName") if live else None) or tug.get("name") or f"SAAM {mmsi}"
        add_tug(name, OWN_EMP, True)

    for company, tugs in (competitor_tugs or {}).items():
        for tug in tugs:
            mmsi = str(tug.get("mmsi"))
            live = by_mmsi.get(mmsi)
            name = (live.get("shipName") if live else None) or tug.get("name") or f"{company} {mmsi}"
            add_tug(name, company, False)

    degree: dict = {}
    for link in links:
        degree[link["source"]] = degree.get(link["source"], 0) + 1
        degree[link["target"]] = degree.get(link["target"], 0) + 1

    node_list = []
    for nid, node in nodes.items():
        node = dict(node)
        node["val"] = 1 + degree.get(nid, 0)
        node_list.append(node)

    return {"nodes": node_list, "links": links}

