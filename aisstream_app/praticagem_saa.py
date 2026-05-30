"""
Leitura pública de https://www.praticagem-rj.com.br/

1. Tabela de **programação** (POB, Navio, Cal, LOA, …) — prioridade.
2. Quadro **Navios na Pedra** (fila CPRJ / zonas) — se a tabela não existir no HTML.

Requer: beautifulsoup4 (HTML com tooltips aninhados).
"""
from __future__ import annotations

import html as html_module
import re
import ssl
import urllib.request
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

DEFAULT_PRATICAGEM_URL = "https://www.praticagem-rj.com.br/"

ZONE_SPAN_RE = re.compile(
    r'<span style="color: white; font-weight: bold;">([^<]{1,64})</span>',
)
SHIP_SPAN_STRICT_RE = re.compile(
    r'<span style="color: green; font-weight: bold; font-size: 12px;">([^<]+)</span>',
    re.I,
)
SHIP_SPAN_LOOSE_RE = re.compile(
    r'<span[^>]+style="[^"]*color:\s*green[^"]*font-weight:\s*bold[^"]*font-size:\s*12px[^"]*"[^>]*>([^<]+)</span>',
    re.I,
)
STATUS_SPAN_STRICT_RE = re.compile(
    r'<span style="font-size: 11px;">([^<]+)</span>',
    re.I,
)
STATUS_SPAN_LOOSE_RE = re.compile(
    r'<span[^>]+style="[^"]*font-size:\s*11px[^"]*"[^>]*>([^<]+)</span>',
    re.I,
)


def _clean(s: str) -> str:
    t = html_module.unescape(s).strip()
    t = re.sub(r"\s+", " ", t)
    return t


def _parse_with_ship_status_res(
    page_html: str,
    ship_re: re.Pattern[str],
    status_re: re.Pattern[str],
    max_gap: int,
) -> list[dict[str, Any]]:
    zones = [(m.start(), _clean(m.group(1))) for m in ZONE_SPAN_RE.finditer(page_html)]
    rows: list[dict[str, Any]] = []
    for sm in ship_re.finditer(page_html):
        st = status_re.search(page_html, sm.end())
        if not st or (st.start() - sm.end()) > max_gap:
            continue
        vessel = _clean(sm.group(1))
        status = _clean(st.group(1))
        if not vessel:
            continue
        zone = "—"
        for zp, zn in zones:
            if zp < sm.start():
                zone = zn
            else:
                break
        rows.append(
            {
                "rowSource": "pedra",
                "zone": zone,
                "vesselName": vessel,
                "status": status,
                "berthName": "",
                "empRb": "",
                "pob": "",
                "cal": "",
                "loa": "",
                "dwt": "",
                "m": "",
                "boca": "",
                "gt": "",
            }
        )
    return rows


def parse_navios_pedra_html(page_html: str) -> list[dict[str, Any]]:
    rows = _parse_with_ship_status_res(
        page_html, SHIP_SPAN_STRICT_RE, STATUS_SPAN_STRICT_RE, 900
    )
    if rows:
        return rows
    return _parse_with_ship_status_res(
        page_html, SHIP_SPAN_LOOSE_RE, STATUS_SPAN_LOOSE_RE, 2500
    )


def _strip_tooltip_noise(td) -> None:
    for div in td.find_all("div"):
        if not isinstance(div, Tag):
            continue
        attrs = getattr(div, "attrs", None) or {}
        cls = attrs.get("class") or []
        cl = " ".join(cls) if isinstance(cls, list) else str(cls)
        if "tooltipDivEscondida" in cl or cl == "tooltipDivEscondida":
            div.decompose()


def parse_programacao_html(page_html: str) -> list[dict[str, Any]]:
    """
    Tabela com cabeçalho span.spanCabecalho «POB» (programação de manobras no site).
    """
    soup = BeautifulSoup(page_html, "html.parser")
    header_span = None
    for sp in soup.find_all("span", class_="spanCabecalho"):
        if sp.get_text(strip=True) == "POB":
            header_span = sp
            break
    if not header_span:
        return []
    header_tr = header_span.find_parent("tr")
    if not header_tr:
        return []
    titles: list[str] = []
    for td in header_tr.find_all("td", recursive=False):
        sp = td.find("span", class_="spanCabecalho")
        titles.append(sp.get_text(strip=True) if sp else "")
    if not any(t == "POB" for t in titles):
        return []

    def cell_val(rowd: dict[str, str], *candidates: str) -> str:
        for c in candidates:
            for k, v in rowd.items():
                if k.strip().lower().replace(".", "") == c.lower().replace(".", ""):
                    s = (v or "").strip()
                    if s:
                        return s
        return ""

    rows_out: list[dict[str, Any]] = []
    for tr in header_tr.find_next_siblings("tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 2:
            continue
        cells: list[str] = []
        for td in tds:
            _strip_tooltip_noise(td)
            txt = td.get_text(" ", strip=True)
            txt = re.sub(r"\s+", " ", txt).strip()
            cells.append(txt)
        n = min(len(titles), len(cells))
        if n < 2:
            continue
        rowd: dict[str, str] = {}
        bd_vals: list[str] = []
        for i in range(n):
            t = titles[i]
            if not t:
                continue
            v = cells[i]
            if t == "BD":
                bd_vals.append(v.strip())
                continue
            rowd[t] = v

        navio = cell_val(rowd, "Navio")
        if not navio:
            continue
        navio = re.sub(r"\s+IMO\s+.*$", "", navio, flags=re.I).strip()

        berth = " │ ".join(
            x
            for x in (
                cell_val(rowd, "De"),
                cell_val(rowd, "Para"),
                cell_val(rowd, "Canal"),
                cell_val(rowd, "CTB"),
            )
            if x
        )

        status = " │ ".join(x for x in bd_vals if x) or ""
        if not status:
            d0 = cell_val(rowd, "De")
            p0 = cell_val(rowd, "Para")
            status = " │ ".join(x for x in (d0, p0) if x) or "—"
        emp = cell_val(rowd, "EMP.RB") or cell_val(rowd, "RB")

        rows_out.append(
            {
                "rowSource": "programacao",
                "vesselName": navio,
                "pob": cell_val(rowd, "POB"),
                "cal": cell_val(rowd, "Cal"),
                "loa": cell_val(rowd, "LOA"),
                "dwt": cell_val(rowd, "DWT"),
                "m": cell_val(rowd, "M"),
                "boca": cell_val(rowd, "Boca"),
                "gt": cell_val(rowd, "GT"),
                "berthName": berth or "—",
                "empRb": emp or "—",
                "status": status[:220] if status else "—",
                "zone": "",
            }
        )
    return rows_out


def fetch_praticagem_home(url: str = DEFAULT_PRATICAGEM_URL, timeout: float = 45.0) -> str:
    ctx = ssl.create_default_context()
    base = url.split("/", 3)
    origin = f"{base[0]}//{base[2]}" if len(base) > 2 else "https://www.praticagem-rj.com.br"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": origin + "/",
            "Cache-Control": "max-age=0",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def fetch_and_parse_navios_pedra(url: str = DEFAULT_PRATICAGEM_URL) -> list[dict[str, Any]]:
    html = fetch_praticagem_home(url=url)
    prog = parse_programacao_html(html)
    if prog:
        return prog
    return parse_navios_pedra_html(html)


def fetch_parse_praticagem_diagnostics(
    url: str = DEFAULT_PRATICAGEM_URL,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    html = fetch_praticagem_home(url=url)
    rows_prog = parse_programacao_html(html)
    rows_pedra = parse_navios_pedra_html(html)
    if rows_prog:
        rows = rows_prog
        source_used = "programacao"
    else:
        rows = rows_pedra
        source_used = "pedra"
    diag: dict[str, Any] = {
        "url": url,
        "htmlChars": len(html),
        "zonesMatched": len(list(ZONE_SPAN_RE.finditer(html))),
        "shipsStrictMatched": len(list(SHIP_SPAN_STRICT_RE.finditer(html))),
        "shipsLooseMatched": len(list(SHIP_SPAN_LOOSE_RE.finditer(html))),
        "hasDivConteudoLateral": "divConteudoLateral" in html,
        "programacaoRows": len(rows_prog),
        "pedraRows": len(rows_pedra),
        "rowsParsed": len(rows),
        "sourceUsed": source_used,
    }
    if html and len(html) < 8000:
        diag["htmlLooksTooSmall"] = True
    return rows, diag
