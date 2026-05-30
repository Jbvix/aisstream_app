import os
import math
import unicodedata
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from dotenv import load_dotenv
import asyncio
import json
import websockets
import time
import threading
import uuid
import urllib.request
import urllib.error
from pathlib import Path
from collections import deque
from websockets.exceptions import ConnectionClosed

import praticagem_saa

load_dotenv()

APP_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = APP_ROOT / "frontend"

PORT = int(os.getenv("PORT", 8080))
AIS_MODE = os.getenv("AIS_MODE", "mock").lower()
AISSTREAM_API_KEY = os.getenv("AISSTREAM_API_KEY", "")
DEFAULT_AREA = os.getenv("DEFAULT_AREA", "rio").lower()
AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream"
SAAM_BGRA_FLEET_NAME = "SAAM-BGRA"
SAAM_BGRA_MMSI_SET = {
    "710020280",  # SAAM ARIES
    "710000348",  # SAAM ITABIRA
    "710021750",  # SAAM CHILE
    "710001593",  # SAAM HOLANDA
    "710016030",  # SAAM LANCELOT
    "710015310",  # SAAM ARTHUR
}
# BBox operacional da Baia de Guanabara (lon/lat aproximados)
GUANABARA_GEOFENCE = {
    "name": "Baia de Guanabara",
    "minLat": -23.08,
    "maxLat": -22.75,
    "minLon": -43.35,
    "maxLon": -43.05,
}
BG_INTERNO_GEOFENCE_ID = "bg-interno-persistente"
BG_INTERNO_GEOFENCE_NAME = "Baia de Guanabara Interno"
LEGACY_GEOFENCE_STORAGE_PATH = APP_ROOT / "data" / "geofences.json"
DASHBOARD_USER_ID = (os.getenv("DASHBOARD_USER_ID") or "default").strip() or "default"
SAAM_MMSI_ABBR = {
    "710020280": "AR",
    "710000348": "IT",
    "710021750": "CH",
    "710001593": "HL",
    "710016030": "LT",
    "710015310": "AT",
}
COMPETITOR_TUGS = {
    "WIL": [
        {"mmsi": "710005290", "name": "LYRA"},
        {"mmsi": "710000009", "name": "HERCULES"},
        {"mmsi": "710000391", "name": "WEZEN"},
        {"mmsi": "710018340", "name": "PEGASUS"},
    ],
    "CAM": [
        {"mmsi": "710009550", "name": "C NEBLINA"},
        {"mmsi": "710008322", "name": "C HARPIA"},
        {"mmsi": "710010250", "name": "C ARRAIAL / C SALVADOR"},
    ],
}
GROK_API_KEY = (os.getenv("XAI_API_KEY") or "").strip()
GROK_MODEL = (os.getenv("XAI_MODEL") or "grok-3-mini").strip()
ASSISTANT_PROFILE = (os.getenv("ASSISTANT_PROFILE") or "hibrido").strip().lower()
# Estatísticas persistidas (tug_geofence_stats.json): só berço e polígono contam manobra + tempo.
# Saída da base rebocador não soma manobra nem horas nesse ficheiro.
SAAM_MANEUVER_STATS_GEOFENCE_TYPES = frozenset({"berco", "polygon"})
# Navio comercial (não SAAM-BGRA) → indicador «manobra SAA» no dashboard (berço/polígono/base)
SAA_MANEUVER_SHIP_CATEGORIES = frozenset(
    {"carga", "petroleiro", "passageiros", "lazer", "pesca", "outros"}
)


def _vessel_matches_saa_maneuver_lamp(vessel):
    if not isinstance(vessel, dict):
        return False
    if bool(vessel.get("isSaamBgra")):
        return False
    cat = vessel.get("shipCategory") or "outros"
    return cat in SAA_MANEUVER_SHIP_CATEGORIES


def _vessel_display_name_for_tooltip(vessel):
    if not isinstance(vessel, dict):
        return "—"
    name = (vessel.get("shipName") or "").strip()
    if name:
        return name
    mmsi = vessel.get("mmsi")
    return f"MMSI {mmsi}" if mmsi is not None else "—"


def _distance_m_approx(v1, v2):
    lat1, lon1 = v1.get("latitude"), v1.get("longitude")
    lat2, lon2 = v2.get("latitude"), v2.get("longitude")
    if not all(isinstance(x, (int, float)) for x in (lat1, lon1, lat2, lon2)):
        return float("inf")
    dy = (float(lat1) - float(lat2)) * 111_320.0
    dx = (float(lon1) - float(lon2)) * 111_320.0
    return (dx * dx + dy * dy) ** 0.5


def _berco_em_manobra_text(inside_geo):
    tugs = [v for v in inside_geo if bool(v.get("isSaamBgra"))]
    ships = [v for v in inside_geo if not bool(v.get("isSaamBgra"))]
    if not tugs:
        return "—"
    if not ships:
        tug_names = ", ".join(_vessel_display_name_for_tooltip(v) for v in tugs[:4])
        return f"{tug_names} (sem navio)"
    pairs = []
    for tug in tugs[:4]:
        nearest_ship = min(ships, key=lambda ship: _distance_m_approx(tug, ship))
        pairs.append(
            f"{_vessel_display_name_for_tooltip(tug)} + {_vessel_display_name_for_tooltip(nearest_ship)}"
        )
    return " | ".join(pairs)

AREAS = {
    "suape": {
        "name": "Suape",
        "center": [-8.393, -34.968],
        "zoom": 11,
        "boundingBoxes": [[[-8.25, -35.15], [-8.55, -34.75]]]
    },
    "santos": {
        "name": "Santos",
        "center": [-23.975, -46.33],
        "zoom": 11,
        "boundingBoxes": [[[-23.82, -46.5], [-24.15, -46.15]]]
    },
    "rio": {
        "name": "Rio de Janeiro",
        "center": [-22.895, -43.165],
        "zoom": 11,
        "boundingBoxes": [[[-22.75, -43.4], [-23.05, -42.95]]]
    },
    "paranagua": {
        "name": "Paranaguá",
        "center": [-25.509, -48.505],
        "zoom": 11,
        "boundingBoxes": [[[-25.35, -48.75], [-25.75, -48.3]]]
    },
    "bahia": {
        "name": "Baía de Todos-os-Santos",
        "center": [-12.900, -38.516],
        "zoom": 11,
        "boundingBoxes": [[[-12.7, -38.8], [-13.1, -38.2]]]
    },
    "mucuripe_pecem": {
        "name": "Mucuripe / Pecem",
        "center": [-3.66, -38.65],
        "zoom": 10,
        "boundingBoxes": [[[-3.40, -38.95], [-3.95, -38.35]]]
    },
    "itaguai": {
        "name": "Itaguai",
        "center": [-22.93, -43.85],
        "zoom": 10,
        "boundingBoxes": [[[-22.70, -44.20], [-23.20, -43.55]]]
    },
    "vitoria": {
        "name": "Vitoria",
        "center": [-20.31, -40.29],
        "zoom": 10,
        "boundingBoxes": [[[-20.10, -40.55], [-20.55, -40.05]]]
    },
    "rio_grande": {
        "name": "Rio Grande",
        "center": [-32.12, -52.10],
        "zoom": 10,
        "boundingBoxes": [[[-31.90, -52.40], [-32.35, -51.80]]]
    },
    "itajai": {
        "name": "Itajai",
        "center": [-26.91, -48.67],
        "zoom": 10,
        "boundingBoxes": [[[-26.70, -48.90], [-27.15, -48.45]]]
    },
    "sao_francisco_do_sul": {
        "name": "Sao Francisco do Sul",
        "center": [-26.24, -48.64],
        "zoom": 10,
        "boundingBoxes": [[[-26.05, -48.85], [-26.45, -48.40]]]
    },
    "rotterdam": {
        "name": "Rotterdam",
        "center": [51.94, 4.14],
        "zoom": 10,
        "boundingBoxes": [[[51.75, 3.80], [52.20, 4.60]]]
    },
    "antwerp_bruges": {
        "name": "Antwerp-Bruges",
        "center": [51.29, 4.32],
        "zoom": 10,
        "boundingBoxes": [[[51.10, 3.95], [51.55, 4.75]]]
    },
    "hamburg": {
        "name": "Hamburg",
        "center": [53.54, 9.96],
        "zoom": 10,
        "boundingBoxes": [[[53.35, 9.55], [53.75, 10.35]]]
    },
    "algeciras": {
        "name": "Algeciras",
        "center": [36.13, -5.45],
        "zoom": 10,
        "boundingBoxes": [[[35.95, -5.85], [36.35, -5.10]]]
    },
    "tangier_med": {
        "name": "Tangier Med",
        "center": [35.88, -5.50],
        "zoom": 10,
        "boundingBoxes": [[[35.70, -5.90], [36.10, -5.10]]]
    },
    "suez": {
        "name": "Suez Canal",
        "center": [30.60, 32.33],
        "zoom": 9,
        "boundingBoxes": [[[29.95, 31.85], [31.10, 32.95]]]
    },
    "jebel_ali": {
        "name": "Jebel Ali",
        "center": [25.02, 55.06],
        "zoom": 10,
        "boundingBoxes": [[[24.80, 54.75], [25.30, 55.35]]]
    },
    "singapore": {
        "name": "Singapore",
        "center": [1.23, 103.84],
        "zoom": 10,
        "boundingBoxes": [[[1.05, 103.55], [1.45, 104.15]]]
    },
    "shanghai": {
        "name": "Shanghai",
        "center": [31.33, 121.75],
        "zoom": 9,
        "boundingBoxes": [[[30.95, 121.20], [31.80, 122.40]]]
    },
    "ningbo_zhoushan": {
        "name": "Ningbo-Zhoushan",
        "center": [29.93, 122.24],
        "zoom": 9,
        "boundingBoxes": [[[29.40, 121.70], [30.45, 122.85]]]
    },
    "shenzhen": {
        "name": "Shenzhen",
        "center": [22.55, 114.20],
        "zoom": 10,
        "boundingBoxes": [[[22.30, 113.80], [22.85, 114.55]]]
    },
    "hong_kong": {
        "name": "Hong Kong",
        "center": [22.30, 114.17],
        "zoom": 10,
        "boundingBoxes": [[[22.15, 113.90], [22.55, 114.45]]]
    },
    "busan": {
        "name": "Busan",
        "center": [35.10, 129.04],
        "zoom": 10,
        "boundingBoxes": [[[34.90, 128.70], [35.35, 129.40]]]
    },
    "colombo": {
        "name": "Colombo",
        "center": [6.95, 79.85],
        "zoom": 10,
        "boundingBoxes": [[[6.75, 79.60], [7.20, 80.10]]]
    },
    "los_angeles_long_beach": {
        "name": "Los Angeles / Long Beach",
        "center": [33.74, -118.24],
        "zoom": 10,
        "boundingBoxes": [[[33.55, -118.60], [34.00, -117.95]]]
    },
    "new_york_new_jersey": {
        "name": "New York / New Jersey",
        "center": [40.64, -74.07],
        "zoom": 10,
        "boundingBoxes": [[[40.40, -74.35], [40.95, -73.70]]]
    },
    "houston": {
        "name": "Houston",
        "center": [29.72, -95.18],
        "zoom": 10,
        "boundingBoxes": [[[29.45, -95.55], [30.05, -94.85]]]
    },
    "panama_canal": {
        "name": "Panama Canal",
        "center": [9.11, -79.66],
        "zoom": 10,
        "boundingBoxes": [[[8.85, -79.95], [9.45, -79.35]]]
    },
    "valparaiso_san_antonio": {
        "name": "Valparaiso / San Antonio",
        "center": [-33.35, -71.64],
        "zoom": 10,
        "boundingBoxes": [[[-33.70, -72.10], [-32.95, -71.30]]]
    },
    "durban": {
        "name": "Durban",
        "center": [-29.87, 31.04],
        "zoom": 10,
        "boundingBoxes": [[[-30.10, 30.70], [-29.55, 31.35]]]
    },
    "sydney_botany": {
        "name": "Sydney (Botany)",
        "center": [-33.95, 151.22],
        "zoom": 10,
        "boundingBoxes": [[[-34.15, 150.95], [-33.65, 151.50]]]
    },
    "brasil_sudeste": {
        "name": "Brasil Sudeste",
        "center": [-23.8, -43.5],
        "zoom": 6,
        "boundingBoxes": [[[-23.3, -42.5], [-24.2, -44.1]]]
    },
    "miami_teste": {
        "name": "Miami (Teste Live)",
        "center": [25.72, -80.04],
        "zoom": 10,
        "boundingBoxes": [[[25.835302, -80.207729], [25.602700, -79.879297]]]
    },
    "mundo_teste": {
        "name": "Mundo (Diagnóstico)",
        "center": [0.0, 0.0],
        "zoom": 2,
        "boundingBoxes": [[[-90, -180], [90, 180]]]
    }
}


from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_area_key = DEFAULT_AREA if DEFAULT_AREA in AREAS else "rio"
current_mode = "live"
live_connected = False
last_error = None
last_ais_message_at = None
total_messages = 0
live_subscription_update_event = asyncio.Event()
last_subscription_update_monotonic = 0.0
vessel_state_by_mmsi = {}
latest_vessel_by_mmsi = {}
recent_vessels = deque(maxlen=4000)
last_vessel_seq = 0
live_worker_task = None
_praticagem_auto_sync_task: asyncio.Task | None = None
live_worker_thread = None
live_worker_lock = threading.Lock()
geofences = []
geofence_lock = threading.Lock()
saam_geofence_stats_lock = threading.Lock()
last_saam_inside_geofences = {}
saam_geofence_sessions = {}
saam_last_position_for_nm = {}
_nm_save_budget = {"n": 0, "last_mono": 0.0}
tug_stats_state = {"byMmsi": {}, "updatedAt": None}
saa_maneuvers_lock = threading.RLock()
saa_maneuvers_list = []


def user_data_dir(user_id: str) -> Path:
    p = APP_ROOT / "data" / "users" / user_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def geofences_file_for_user(user_id: str) -> Path:
    return user_data_dir(user_id) / "geofences.json"


def ensure_data_dir():
    (APP_ROOT / "data").mkdir(parents=True, exist_ok=True)


def migrate_legacy_geofences_if_needed(user_id: str):
    dest = geofences_file_for_user(user_id)
    if dest.exists():
        return
    if LEGACY_GEOFENCE_STORAGE_PATH.exists():
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(LEGACY_GEOFENCE_STORAGE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass


def _normalize_text(value) -> str:
    return (
        unicodedata.normalize("NFD", str(value or ""))
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
        .lower()
    )


def _is_bg_interno_geofence(geofence: dict) -> bool:
    if not isinstance(geofence, dict):
        return False
    if str(geofence.get("id") or "").strip() == BG_INTERNO_GEOFENCE_ID:
        return True
    return _normalize_text(geofence.get("name")) == _normalize_text(BG_INTERNO_GEOFENCE_NAME)


def _default_bg_interno_geometry():
    min_lat = GUANABARA_GEOFENCE["minLat"]
    max_lat = GUANABARA_GEOFENCE["maxLat"]
    min_lon = GUANABARA_GEOFENCE["minLon"]
    max_lon = GUANABARA_GEOFENCE["maxLon"]
    return {
        "coordinates": [
            [max_lat, min_lon],
            [max_lat, max_lon],
            [min_lat, max_lon],
            [min_lat, min_lon],
        ]
    }


def ensure_bg_interno_geofence():
    changed = False
    target = None
    for g in geofences:
        if _is_bg_interno_geofence(g):
            target = g
            break
    if target is None:
        now = get_now_iso()
        geofences.append(
            {
                "id": BG_INTERNO_GEOFENCE_ID,
                "name": BG_INTERNO_GEOFENCE_NAME,
                "type": "polygon",
                "geometry": _default_bg_interno_geometry(),
                "fleetScope": "all",
                "isActive": True,
                "color": "#4aa8ff",
                "persistent": True,
                "createdAt": now,
                "updatedAt": now,
            }
        )
        changed = True
    else:
        if target.get("id") != BG_INTERNO_GEOFENCE_ID:
            target["id"] = BG_INTERNO_GEOFENCE_ID
            changed = True
        if target.get("name") != BG_INTERNO_GEOFENCE_NAME:
            target["name"] = BG_INTERNO_GEOFENCE_NAME
            changed = True
        if target.get("type") != "polygon":
            target["type"] = "polygon"
            changed = True
        if not isinstance(target.get("geometry"), dict) or not target.get("geometry", {}).get("coordinates"):
            target["geometry"] = _default_bg_interno_geometry()
            changed = True
        if target.get("fleetScope") != "all":
            target["fleetScope"] = "all"
            changed = True
        if target.get("isActive") is not True:
            target["isActive"] = True
            changed = True
        if target.get("persistent") is not True:
            target["persistent"] = True
            changed = True
        if changed:
            target["updatedAt"] = get_now_iso()
    return changed


def load_geofences():
    global geofences
    ensure_data_dir()
    uid = DASHBOARD_USER_ID
    migrate_legacy_geofences_if_needed(uid)
    path = geofences_file_for_user(uid)
    if not path.exists():
        geofences = []
        return
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(content, list):
            geofences = content
        else:
            geofences = []
    except Exception:
        geofences = []
    if ensure_bg_interno_geofence():
        save_geofences()


def ensure_geofences_loaded():
    """Lazy-load defensivo para ambientes Passenger onde startup pode não hidratar estado."""
    if geofences:
        return
    with geofence_lock:
        if geofences:
            return
        load_geofences()


def save_geofences():
    uid = DASHBOARD_USER_ID
    path = geofences_file_for_user(uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(geofences, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def tug_stats_file_for_user(user_id: str) -> Path:
    return user_data_dir(user_id) / "tug_geofence_stats.json"


def load_tug_stats():
    global tug_stats_state
    path = tug_stats_file_for_user(DASHBOARD_USER_ID)
    if not path.exists():
        tug_stats_state = {"byMmsi": {}, "updatedAt": get_now_iso()}
        return
    try:
        tug_stats_state = json.loads(path.read_text(encoding="utf-8"))
        if "byMmsi" not in tug_stats_state:
            tug_stats_state["byMmsi"] = {}
    except Exception:
        tug_stats_state = {"byMmsi": {}, "updatedAt": get_now_iso()}


def save_tug_stats():
    path = tug_stats_file_for_user(DASHBOARD_USER_ID)
    with saam_geofence_stats_lock:
        tug_stats_state["updatedAt"] = get_now_iso()
        path.write_text(
            json.dumps(tug_stats_state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def saa_maneuvers_file_for_user(user_id: str) -> Path:
    return user_data_dir(user_id) / "saa_maneuvers.json"


def strategy_memory_file_for_user(user_id: str) -> Path:
    return user_data_dir(user_id) / "strategy_memory.json"


def schedule_monitor_file_for_user(user_id: str) -> Path:
    return user_data_dir(user_id) / "saa_schedule_monitor.json"


def load_saa_maneuvers():
    global saa_maneuvers_list
    path = saa_maneuvers_file_for_user(DASHBOARD_USER_ID)
    if not path.exists():
        saa_maneuvers_list = []
        return
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        saa_maneuvers_list = raw if isinstance(raw, list) else raw.get("items", [])
    except Exception:
        saa_maneuvers_list = []


def ensure_saa_maneuvers_loaded():
    """Se a lista em memória estiver vazia, relê saa_maneuvers.json (startup parcial ou processo sem on_event)."""
    path = saa_maneuvers_file_for_user(DASHBOARD_USER_ID)
    if not path.exists():
        return
    with saa_maneuvers_lock:
        if saa_maneuvers_list:
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            data = raw if isinstance(raw, list) else raw.get("items", [])
            if data:
                saa_maneuvers_list[:] = data
        except Exception:
            pass


def save_saa_maneuvers():
    path = saa_maneuvers_file_for_user(DASHBOARD_USER_ID)
    with saa_maneuvers_lock:
        path.write_text(json.dumps(saa_maneuvers_list, ensure_ascii=False, indent=2), encoding="utf-8")


def _saa_maneuver_dedupe_key(item: dict):
    def norm(v):
        return str(v or "").strip().upper()

    return (
        norm(item.get("source")),
        norm(item.get("pob")),
        norm(item.get("vesselName")),
        norm(item.get("berthName")),
        norm(item.get("empRb")),
        norm(item.get("status")),
        norm(item.get("cal")),
        norm(item.get("loa")),
        norm(item.get("boca")),
        norm(item.get("dwt")),
        norm(item.get("gt")),
        norm(item.get("m")),
    )


def _dedupe_saa_maneuvers(items):
    seen = set()
    out = []
    for item in items or []:
        key = _saa_maneuver_dedupe_key(item if isinstance(item, dict) else {})
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def load_strategy_memory():
    path = strategy_memory_file_for_user(DASHBOARD_USER_ID)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []
    except Exception:
        return []


def append_strategy_memory(note: str, author: str = "user"):
    note = (note or "").strip()
    if not note:
        return
    items = load_strategy_memory()
    items.insert(0, {"at": get_now_iso(), "author": author, "note": note})
    path = strategy_memory_file_for_user(DASHBOARD_USER_ID)
    path.write_text(json.dumps(items[:200], ensure_ascii=False, indent=2), encoding="utf-8")


def _saa_dim_defaults() -> dict:
    """Dimensões / programação; vazios na fila «Pedra» sem tabela."""
    return {"pob": "", "cal": "", "loa": "", "dwt": "", "m": "", "boca": "", "gt": ""}


def _saa_dims_from_payload(payload: dict) -> dict:
    d = _saa_dim_defaults()
    for k in d:
        v = payload.get(k)
        if v is not None and str(v).strip():
            d[k] = str(v).strip()
    return d


def _haversine_nm(lat1, lon1, lat2, lon2):
    """Distância ortodrómica aproximada (esfera) em milhas náuticas (MN)."""
    r_nm = 3440.065  # raio médio da Terra em MN
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(h), math.sqrt(max(0.0, 1.0 - h)))
    return r_nm * c


def _parse_vessel_timestamp_unix(vessel):
    raw = vessel.get("timestamp")
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def _accumulate_saam_exit(mmsi, geofence_id, geofence_name, duration_sec, vessel):
    bym = tug_stats_state.setdefault("byMmsi", {})
    ent = bym.setdefault(
        mmsi,
        {
            "abbr": SAAM_MMSI_ABBR.get(mmsi, mmsi[-3:]),
            "name": vessel.get("shipName") or "",
            "totalSeconds": 0.0,
            "totalManeuvers": 0,
            "totalNauticalMiles": 0.0,
            "byGeofence": {},
        },
    )
    ent["name"] = vessel.get("shipName") or ent.get("name")
    gf = ent["byGeofence"].setdefault(
        geofence_id,
        {"name": geofence_name, "seconds": 0.0, "maneuvers": 0},
    )
    gf["name"] = geofence_name
    gf["seconds"] = float(gf.get("seconds", 0)) + duration_sec
    gf["maneuvers"] = int(gf.get("maneuvers", 0)) + 1
    ent["totalSeconds"] = float(ent.get("totalSeconds", 0)) + duration_sec
    ent["totalManeuvers"] = int(ent.get("totalManeuvers", 0)) + 1


def _bump_saam_nautical_miles(mmsi, vessel, delta_nm):
    if delta_nm <= 0:
        return False
    bym = tug_stats_state.setdefault("byMmsi", {})
    ent = bym.setdefault(
        mmsi,
        {
            "abbr": SAAM_MMSI_ABBR.get(mmsi, mmsi[-3:]),
            "name": vessel.get("shipName") or "",
            "totalSeconds": 0.0,
            "totalManeuvers": 0,
            "totalNauticalMiles": 0.0,
            "byGeofence": {},
        },
    )
    ent["name"] = vessel.get("shipName") or ent.get("name")
    ent["totalNauticalMiles"] = float(ent.get("totalNauticalMiles", 0)) + float(delta_nm)
    return True


def _maybe_persist_nm_stats():
    global _nm_save_budget
    _nm_save_budget["n"] = _nm_save_budget.get("n", 0) + 1
    now = time.monotonic()
    last = float(_nm_save_budget.get("last_mono", 0.0))
    if _nm_save_budget["n"] >= 35 or (now - last) >= 150.0:
        _nm_save_budget["n"] = 0
        _nm_save_budget["last_mono"] = now
        save_tug_stats()


def update_saam_nautical_miles(vessel):
    """Soma milhas náuticas percorridas entre posições AIS consecutivas (rebocadores SAAM-BGRA)."""
    if not vessel.get("isSaamBgra"):
        return
    mmsi = str(vessel.get("mmsi"))
    lat = vessel.get("latitude")
    lon = vessel.get("longitude")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return
    lat = float(lat)
    lon = float(lon)
    t_cur = _parse_vessel_timestamp_unix(vessel)
    try:
        sog = float(vessel.get("sog") or 0)
    except (TypeError, ValueError):
        sog = 0.0

    did_nm = False
    mono_now = time.monotonic()
    with saam_geofence_stats_lock:
        prev = saam_last_position_for_nm.get(mmsi)
        saam_last_position_for_nm[mmsi] = {
            "lat": lat,
            "lon": lon,
            "t_ais": t_cur,
            "sog": sog,
            "mono": mono_now,
        }
        if not prev:
            return
        lat0, lon0 = float(prev["lat"]), float(prev["lon"])
        t0 = prev.get("t_ais")
        if t_cur is not None and t0 is not None:
            dt_s = t_cur - t0
        else:
            pm = prev.get("mono")
            dt_s = (mono_now - float(pm)) if pm is not None else 0.0
        if dt_s <= 0 or dt_s > 6 * 3600:
            return
        nm = _haversine_nm(lat0, lon0, lat, lon)
        sog_ref = max(sog, float(prev.get("sog") or 0), 2.0)
        max_nm = max(0.08, min(100.0, (dt_s / 3600.0) * max(28.0, sog_ref * 1.6)))
        if nm > max_nm:
            return
        if nm < 1e-6:
            return
        did_nm = _bump_saam_nautical_miles(mmsi, vessel, nm)

    if did_nm:
        _maybe_persist_nm_stats()


def update_saam_fleet_geofence_stats(vessel):
    if not vessel.get("isSaamBgra"):
        return
    mmsi = str(vessel.get("mmsi"))
    now = time.time()
    inside_ids = set()
    id_to_name = {}
    valid_maneuver_gids = set()
    with geofence_lock:
        maneuver_geofences = [
            g
            for g in geofences
            if g.get("isActive", True) and g.get("type") in SAAM_MANEUVER_STATS_GEOFENCE_TYPES
        ]
        for g in maneuver_geofences:
            gid = g.get("id")
            if gid:
                valid_maneuver_gids.add(gid)
        for g in maneuver_geofences:
            if not geofence_matches_vessel_scope(vessel, g):
                continue
            gid = g.get("id")
            if not gid:
                continue
            id_to_name[gid] = g.get("name", gid)
            if is_inside_geofence(vessel, g):
                inside_ids.add(gid)
    had_exit = False
    with saam_geofence_stats_lock:
        for key in list(saam_geofence_sessions.keys()):
            if key[0] == mmsi and key[1] not in valid_maneuver_gids:
                saam_geofence_sessions.pop(key, None)
        prev_stored = last_saam_inside_geofences.get(mmsi, set())
        prev = {gid for gid in prev_stored if gid in valid_maneuver_gids}
        for gid in prev - inside_ids:
            had_exit = True
            sess = saam_geofence_sessions.pop((mmsi, gid), None)
            if sess:
                dt = max(0.0, now - sess["t0"])
                _accumulate_saam_exit(mmsi, gid, id_to_name.get(gid, str(gid)), dt, vessel)
        for gid in inside_ids - prev:
            saam_geofence_sessions[(mmsi, gid)] = {"t0": now}
        last_saam_inside_geofences[mmsi] = set(inside_ids)
    if had_exit:
        save_tug_stats()


def point_in_polygon(latitude, longitude, polygon):
    # polygon: [[lat, lon], [lat, lon], ...]
    if not polygon or len(polygon) < 3:
        return False
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        yi, xi = polygon[i][0], polygon[i][1]
        yj, xj = polygon[j][0], polygon[j][1]
        intersects = ((yi > latitude) != (yj > latitude)) and (
            longitude < (xj - xi) * (latitude - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def is_inside_geofence(vessel, geofence):
    geometry = geofence.get("geometry") or {}
    gtype = geofence.get("type")
    latitude = vessel.get("latitude")
    longitude = vessel.get("longitude")
    if latitude is None or longitude is None:
        return False
    if gtype in {"berco", "base_rebocador", "polygon"}:
        polygon = geometry.get("coordinates") or []
        return point_in_polygon(latitude, longitude, polygon)
    if gtype == "circle":
        center = geometry.get("center") or []
        radius_m = geometry.get("radiusMeters") or 0
        if len(center) != 2 or radius_m <= 0:
            return False
        # aprox. metros por grau
        dy = (latitude - center[0]) * 111_320
        dx = (longitude - center[1]) * 111_320
        return (dx * dx + dy * dy) ** 0.5 <= radius_m
    return False


def geofence_matches_vessel_scope(vessel, geofence):
    scope = geofence.get("fleetScope", "all")
    if scope == "all":
        return True
    if scope == SAAM_BGRA_FLEET_NAME:
        return bool(vessel.get("isSaamBgra"))
    return False


def get_vessel_geofences(vessel):
    ensure_geofences_loaded()
    names = []
    with geofence_lock:
        active_geofences = [g for g in geofences if g.get("isActive", True)]
    for geofence in active_geofences:
        if not geofence_matches_vessel_scope(vessel, geofence):
            continue
        if is_inside_geofence(vessel, geofence):
            names.append(geofence.get("name", "Sem nome"))
    return names


def vessel_in_rebocador_base(vessel):
    """Dentro de algum geofence ativo tipo base_rebocador (escopo respeitado)."""
    ensure_geofences_loaded()
    with geofence_lock:
        active_geofences = [g for g in geofences if g.get("isActive", True)]
    for geofence in active_geofences:
        if geofence.get("type") != "base_rebocador":
            continue
        if not geofence_matches_vessel_scope(vessel, geofence):
            continue
        if is_inside_geofence(vessel, geofence):
            return True
    return False


def build_geofence_occupancy():
    ensure_geofences_loaded()
    with geofence_lock:
        active_geofences = [g for g in geofences if g.get("isActive", True)]
    vessels = list(latest_vessel_by_mmsi.values())
    occupancy = []
    for geofence in active_geofences:
        inside = []
        for vessel in vessels:
            if not geofence_matches_vessel_scope(vessel, geofence):
                continue
            if is_inside_geofence(vessel, geofence):
                inside.append(
                    {
                        "mmsi": vessel.get("mmsi"),
                        "shipName": vessel.get("shipName"),
                        "shipCategory": vessel.get("shipCategory"),
                        "fleet": vessel.get("fleet"),
                        "timestamp": vessel.get("timestamp"),
                        "heading": vessel.get("heading"),
                        "course": vessel.get("course"),
                        "isSaamBgra": bool(vessel.get("isSaamBgra")),
                        "latitude": vessel.get("latitude"),
                        "longitude": vessel.get("longitude"),
                    }
                )
        occupancy.append(
            {
                "geofenceId": geofence.get("id"),
                "name": geofence.get("name"),
                "type": geofence.get("type"),
                "fleetScope": geofence.get("fleetScope", "all"),
                "vesselCount": len(inside),
                "insideVessels": inside,
            }
        )
    return occupancy


def build_live_subscription():
    return {
        "APIKey": AISSTREAM_API_KEY,
        "BoundingBoxes": AREAS[current_area_key]["boundingBoxes"],
        "FilterMessageTypes": [
            "PositionReport",
            "StandardClassBPositionReport",
            "ExtendedClassBPositionReport",
            "ShipStaticData",
            "StaticDataReport",
        ],
    }


def ensure_live_worker_started():
    global live_worker_thread
    if current_mode != "live" or not AISSTREAM_API_KEY:
        return
    with live_worker_lock:
        if live_worker_thread and live_worker_thread.is_alive():
            return
        live_worker_thread = threading.Thread(
            target=lambda: asyncio.run(live_background_worker()),
            daemon=True,
            name="ais-live-worker",
        )
        live_worker_thread.start()


def normalize_ship_type_code(metadata, message_body):
    report_b = message_body.get("ReportB") if isinstance(message_body, dict) else None
    raw_type = (
        metadata.get("ShipType")
        or metadata.get("ship_type")
        or (report_b.get("ShipType") if isinstance(report_b, dict) else None)
        or message_body.get("TypeAndCargo")
        or message_body.get("ShipType")
        or message_body.get("Type")
    )
    try:
        if raw_type is None or raw_type == "":
            return None
        return int(raw_type)
    except Exception:
        return None


def infer_ship_category(ship_type_code, ship_name):
    if ship_type_code is not None:
        if 30 <= ship_type_code <= 39:
            if ship_type_code in [36, 37]:
                return "lazer"
            return "pesca"
        if 50 <= ship_type_code <= 59:
            return "rebocador_servico"
        if 60 <= ship_type_code <= 69:
            return "passageiros"
        if 70 <= ship_type_code <= 79:
            return "carga"
        if 80 <= ship_type_code <= 89:
            return "petroleiro"

    name = (ship_name or "").upper()
    if (
        "TUG" in name
        or "REBOC" in name
        or "AHTS" in name
        or "PSV" in name
        or "OSRV" in name
        or "SUPPLY" in name
        or "SVITZER" in name
        or "SAAM" in name
        or "CBO" in name
        or "HOS " in name
    ):
        return "rebocador_servico"
    if "TANK" in name or "PETRO" in name:
        return "petroleiro"
    if "CARGO" in name or "BULK" in name or "CONTAINER" in name or "BARGE" in name:
        return "carga"
    if "FISH" in name or "PESCA" in name:
        return "pesca"
    if "PASSENGER" in name or "FERRY" in name or "CATAMARAN" in name or "CAT " in name:
        return "passageiros"
    return "outros"


def _dim_segment(value):
    try:
        if value is None:
            return None
        v = int(value)
        if v < 0 or v > 511:
            return None
        return v
    except Exception:
        return None


def extract_ship_dimensions_meters(message_type, message_body):
    """
    Retorna (length_m, beam_m) quando AIS traz dimensões em metros (A/B/C/D).
    LOA ~= A + B, Boca ~= C + D.
    """
    dim = None
    if isinstance(message_body, dict):
        dim = message_body.get("Dimension") or message_body.get("dimension")
    if not isinstance(dim, dict):
        return None, None
    a = _dim_segment(dim.get("A"))
    b = _dim_segment(dim.get("B"))
    c = _dim_segment(dim.get("C"))
    d = _dim_segment(dim.get("D"))
    if a is None or b is None:
        return None, None
    length_m = float(a + b)
    beam_m = None
    if c is not None and d is not None:
        beam_m = float(c + d)
    if length_m <= 0 or length_m > 600:
        return None, beam_m
    if beam_m is not None and (beam_m <= 0 or beam_m > 120):
        beam_m = None
    return length_m, beam_m


def estimate_length_from_category(ship_category):
    """Fallback visual quando não há dimensão AIS (metros aproximados)."""
    if ship_category == "rebocador_servico":
        return 32.0
    if ship_category == "pesca":
        return 28.0
    if ship_category == "lazer":
        return 18.0
    if ship_category == "passageiros":
        return 140.0
    if ship_category == "carga":
        return 220.0
    if ship_category == "petroleiro":
        return 250.0
    return 90.0


def push_recent_vessel(vessel_payload):
    global last_vessel_seq
    last_vessel_seq += 1
    item = dict(vessel_payload)
    item["_seq"] = last_vessel_seq
    recent_vessels.append(item)


def classify_geofence(latitude, longitude):
    if latitude is None or longitude is None:
        return None
    if (
        GUANABARA_GEOFENCE["minLat"] <= latitude <= GUANABARA_GEOFENCE["maxLat"]
        and GUANABARA_GEOFENCE["minLon"] <= longitude <= GUANABARA_GEOFENCE["maxLon"]
    ):
        return GUANABARA_GEOFENCE["name"]
    return None


# --- REST endpoints ---
@app.get("/api/status")
def get_status(expand: str | None = None):
    ensure_live_worker_started()
    out = {
        "app": "KRATOS - Inteligência Naval Estratégica",
        "version": "1.0.0",
        "mode": current_mode,
        "area": AREAS.get(current_area_key, {}),
        "areaKey": current_area_key,
        "liveConnected": live_connected,
        "lastError": last_error,
        "lastAisMessageAt": last_ais_message_at,
        "totalMessages": total_messages,
    }
    if expand == "dashboard":
        out["dashboard"] = build_dashboard_overview_dict()
    return out


async def _sync_saa_from_praticagem_impl():
    """
    Substitui apenas entradas com source=praticagem por uma leitura atual do site público.
    Entradas manuais (sem source ou source diferente) mantêm-se.
    """
    url = (os.getenv("PRATICAGEM_RJ_URL") or praticagem_saa.DEFAULT_PRATICAGEM_URL).strip()
    try:
        rows, parse_diag = await asyncio.to_thread(
            praticagem_saa.fetch_parse_praticagem_diagnostics, url
        )
    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": f"Falha ao aceder Praticagem: {e}"},
            status_code=502,
        )
    if not rows:
        return {
            "ok": True,
            "imported": 0,
            "warning": (
                "Nenhuma linha extraída. Verifique PRATICAGEM_RJ_URL, firewall ou bloqueio do site ao servidor; "
                "veja parseDiagnostics."
            ),
            "parseDiagnostics": parse_diag,
        }
    now = get_now_iso()
    new_items = []
    for r in rows:
        dims = _saa_dim_defaults()
        for k in dims:
            if r.get(k):
                dims[k] = str(r[k]).strip()
        if r.get("rowSource") == "programacao":
            new_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "vesselName": r.get("vesselName") or "—",
                    "berthName": (r.get("berthName") or "").strip() or "—",
                    "empRb": (r.get("empRb") or "").strip() or "—",
                    "status": (r.get("status") or "").strip() or "—",
                    "note": "Fonte: praticagem-rj.com.br (programação pública)",
                    "source": "praticagem",
                    "recordedAt": now,
                    **dims,
                }
            )
        else:
            new_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "vesselName": r.get("vesselName") or "—",
                    "berthName": f"Pedra / {r.get('zone', '—')}",
                    "empRb": (r.get("empRb") or "SAA").strip() or "SAA",
                    "status": (r.get("status") or "").strip() or "—",
                    "note": "Fonte: praticagem-rj.com.br (fila na Pedra)",
                    "source": "praticagem",
                    "recordedAt": now,
                    **dims,
                }
            )
    new_items = _dedupe_saa_maneuvers(new_items)
    with saa_maneuvers_lock:
        kept = [x for x in saa_maneuvers_list if x.get("source") != "praticagem"]
        saa_maneuvers_list[:] = new_items + kept
        save_saa_maneuvers()
    zones = sorted({(r.get("zone") or "").strip() for r in rows if (r.get("zone") or "").strip()})
    return {
        "ok": True,
        "imported": len(new_items),
        "zones": zones,
        "parseDiagnostics": parse_diag,
    }


@app.post("/api/status/sync-praticagem-saa")
async def sync_saa_maneuvers_from_praticagem_status_path():
    return await _sync_saa_from_praticagem_impl()


@app.post("/api/praticagem/saa-sync")
async def sync_saa_maneuvers_from_praticagem_short_path():
    return await _sync_saa_from_praticagem_impl()


@app.post("/api/dashboard/saa-maneuvers/sync-praticagem")
async def sync_saa_maneuvers_from_praticagem_dashboard_api():
    return await _sync_saa_from_praticagem_impl()


@app.post("/dashboard/api/saa-maneuvers/sync-praticagem")
async def sync_saa_maneuvers_from_praticagem_under_dashboard():
    return await _sync_saa_from_praticagem_impl()


@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/api/areas")
def get_areas():
    ensure_live_worker_started()
    return {"areas": AREAS, "currentAreaKey": current_area_key}

@app.get("/api/vessels")
def get_vessels(since: int = 0, limit: int = 300, snapshot: bool = False):
    ensure_live_worker_started()
    if snapshot:
        items = []
        for v in latest_vessel_by_mmsi.values():
            if not isinstance(v, dict):
                continue
            items.append({k: val for k, val in v.items() if k != "raw"})
        return {
            "vessels": items,
            "lastSeq": last_vessel_seq,
            "count": len(items),
        }
    items = [v for v in recent_vessels if v.get("_seq", 0) > since]
    if limit > 0:
        items = items[-limit:]
    current_seq = recent_vessels[-1]["_seq"] if recent_vessels else since
    return {
        "vessels": items,
        "lastSeq": current_seq,
        "count": len(items)
    }


def _dashboard_geofence_status_rows():
    ensure_geofences_loaded()
    occ = {o.get("geofenceId"): o for o in build_geofence_occupancy()}
    with geofence_lock:
        snapshot = list(geofences)
    vessels_full = list(latest_vessel_by_mmsi.values())
    # Linhas «base_rebocador»: SAA acende também se houver navio SAA em qualquer berço **ativo**
    # (geometria só; escopo «SAAM-BGRA» não esconde navio comercial do indicador SAA)
    saa_in_any_berco = False
    for g in snapshot:
        if g.get("type") != "berco" or not g.get("isActive", True):
            continue
        inside_geo_b = [v for v in vessels_full if is_inside_geofence(v, g)]
        if any(_vessel_matches_saa_maneuver_lamp(v) for v in inside_geo_b):
            saa_in_any_berco = True
            break

    rows = []
    for g in snapshot:
        gid = g.get("id")
        o = occ.get(gid, {})
        inside = o.get("insideVessels", [])
        gtype = g.get("type")
        active = bool(g.get("isActive", True))
        if active:
            inside_geo = [v for v in vessels_full if is_inside_geofence(v, g)]
            lamp_saam = any(bool(v.get("isSaamBgra")) for v in inside_geo)
            local_saa = any(_vessel_matches_saa_maneuver_lamp(v) for v in inside_geo)
        else:
            lamp_saam = False
            local_saa = False
        if gtype in ("berco", "polygon"):
            lamp_saa = local_saa
        elif gtype == "base_rebocador":
            lamp_saa = local_saa or saa_in_any_berco
        else:
            lamp_saa = False

        gname = (g.get("name") or "").strip().lower()
        if gname == "base brasco":
            em_manobra = "stand-by"
        elif gtype == "berco" and active:
            em_manobra = _berco_em_manobra_text(inside_geo)
        else:
            em_manobra = "—"

        lamp_saam_names: list[str] = []
        lamp_saa_names: list[str] = []
        if active:
            lamp_saam_names = [
                _vessel_display_name_for_tooltip(v)
                for v in inside_geo
                if bool(v.get("isSaamBgra"))
            ]
            lamp_saam_names = list(dict.fromkeys(lamp_saam_names))[:18]

            if gtype in ("berco", "polygon"):
                lamp_saa_names = [
                    _vessel_display_name_for_tooltip(v)
                    for v in inside_geo
                    if _vessel_matches_saa_maneuver_lamp(v)
                ]
                lamp_saa_names = list(dict.fromkeys(lamp_saa_names))[:18]
            elif gtype == "base_rebocador" and lamp_saa:
                seen: set[str] = set()
                for v in inside_geo:
                    if not _vessel_matches_saa_maneuver_lamp(v):
                        continue
                    label = _vessel_display_name_for_tooltip(v)
                    if label not in seen:
                        seen.add(label)
                        lamp_saa_names.append(label)
                if saa_in_any_berco:
                    for gb in snapshot:
                        if gb.get("type") != "berco" or not gb.get("isActive", True):
                            continue
                        bname = (gb.get("name") or "Berço").strip() or "Berço"
                        for v in vessels_full:
                            if not is_inside_geofence(v, gb):
                                continue
                            if not _vessel_matches_saa_maneuver_lamp(v):
                                continue
                            label = f"{bname} — {_vessel_display_name_for_tooltip(v)}"
                            if label not in seen:
                                seen.add(label)
                                lamp_saa_names.append(label)
                                if len(lamp_saa_names) >= 24:
                                    break
                        if len(lamp_saa_names) >= 24:
                            break

        rows.append(
            {
                "id": gid,
                "name": g.get("name"),
                "type": g.get("type"),
                "fleetScope": g.get("fleetScope", "all"),
                "isActive": bool(g.get("isActive", True)),
                "vesselCount": o.get("vesselCount", 0),
                "insideVessels": inside,
                "lampSaaManeuver": lamp_saa,
                "lampSaamInside": lamp_saam,
                "lampSaaNames": lamp_saa_names,
                "lampSaamNames": lamp_saam_names,
                "emManobra": em_manobra,
            }
        )
    return rows


def _in_maneuver_geofence(vessel, geofence_snapshot):
    for g in geofence_snapshot:
        if not g.get("isActive", True):
            continue
        if g.get("type") not in ("berco", "polygon"):
            continue
        try:
            if is_inside_geofence(vessel, g):
                return g
        except Exception:
            continue
    return None


def _competitor_status_rows(geofence_snapshot):
    rows = []
    for company, tugs in COMPETITOR_TUGS.items():
        for tug in tugs:
            mmsi = tug.get("mmsi")
            vessel = latest_vessel_by_mmsi.get(mmsi) if mmsi else None
            if vessel:
                geo = _in_maneuver_geofence(vessel, geofence_snapshot)
                geofence_name = geo.get("name", "—") if geo else "—"
                manobra = bool(geo)
                ship_name = (vessel.get("shipName") or "").strip() or tug.get("name", "")
                lat = vessel.get("latitude")
                lon = vessel.get("longitude")
            else:
                geofence_name = "—"
                manobra = False
                ship_name = tug.get("name", "")
                lat = None
                lon = None
            rows.append(
                {
                    "company": company,
                    "mmsi": mmsi,
                    "name": ship_name,
                    "insideManeuverGeofence": manobra,
                    "maneuverGeofenceName": geofence_name,
                    "latitude": lat,
                    "longitude": lon,
                }
            )
    return rows


def _market_share_rows(saa_snapshot):
    counts = {}
    for item in saa_snapshot:
        key = str(item.get("empRb") or "N/A").strip().upper() or "N/A"
        counts[key] = counts.get(key, 0) + 1
    total = sum(counts.values())
    rows = []
    for key, cnt in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        share = (100.0 * cnt / total) if total else 0.0
        rows.append({"empRb": key, "count": cnt, "sharePct": round(share, 2)})
    return {"rows": rows, "total": total}


def _parse_recorded_at_iso(value):
    if not value:
        return None
    try:
        txt = str(value).strip()
        if txt.endswith("Z"):
            txt = txt[:-1] + "+00:00"
        return datetime.fromisoformat(txt)
    except Exception:
        return None


def _market_share_windows(saa_snapshot):
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    w7 = now.timestamp() - 7 * 86400
    w30 = now.timestamp() - 30 * 86400

    today_items = []
    w7_items = []
    w30_items = []
    for item in saa_snapshot:
        dt = _parse_recorded_at_iso(item.get("recordedAt"))
        if dt is None:
            continue
        ts = dt.timestamp()
        if dt >= midnight:
            today_items.append(item)
        if ts >= w7:
            w7_items.append(item)
        if ts >= w30:
            w30_items.append(item)
    return {
        "today": _market_share_rows(today_items),
        "last7d": _market_share_rows(w7_items),
        "last30d": _market_share_rows(w30_items),
    }


def _estimate_tugs_required(maneuver):
    def _f(v):
        if v is None:
            return 0.0
        txt = str(v).replace(",", ".").strip()
        try:
            return float(txt)
        except Exception:
            return 0.0

    loa = _f(maneuver.get("loa"))
    dwt = _f(maneuver.get("dwt"))
    if loa >= 300 or dwt >= 100000:
        return 4
    if loa >= 230 or dwt >= 60000:
        return 3
    if loa > 0:
        return 2
    return 2


def _parse_pob_to_datetime(pob):
    s = str(pob or "").strip()
    if not s:
        return None
    m = None
    # dd/mm HH:MM
    try:
        import re

        m = re.match(r"^(\d{1,2})/(\d{1,2})[^\d]?(\d{1,2}):(\d{2})", s)
        if not m:
            return None
        day, mon, hh, mm = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        y = datetime.now().year
        dt = datetime(y, mon, day, hh, mm)
        # ajuste simples de virada de ano
        if dt.timestamp() < datetime.now().timestamp() - 14 * 86400:
            dt = datetime(y + 1, mon, day, hh, mm)
        return dt
    except Exception:
        return None


def _simultaneous_maneuvers_summary(saa_snapshot):
    buckets = {}
    for item in saa_snapshot:
        dt = _parse_pob_to_datetime(item.get("pob"))
        if not dt:
            continue
        key = dt.strftime("%Y-%m-%d %H:00")
        buckets.setdefault(key, []).append(item)
    rows = []
    for key, items in buckets.items():
        if len(items) < 2:
            continue
        tug_demand = sum(_estimate_tugs_required(x) for x in items)
        rows.append(
            {
                "timeSlot": key,
                "maneuvers": len(items),
                "estimatedTugsNeeded": tug_demand,
                "vessels": [x.get("vesselName", "—") for x in items[:10]],
            }
        )
    rows.sort(key=lambda x: x["timeSlot"])
    return rows[:24]


def _schedule_row_key_without_pob(item):
    return "|".join(
        [
            str(item.get("vesselName") or "").strip().upper(),
            str(item.get("berthName") or "").strip().upper(),
            str(item.get("empRb") or "").strip().upper(),
            str(item.get("m") or "").strip().upper(),
            str(item.get("loa") or "").strip(),
            str(item.get("dwt") or "").strip(),
            str(item.get("status") or "").strip().upper(),
        ]
    )


def _schedule_signature(item):
    return _schedule_row_key_without_pob(item) + "|" + str(item.get("pob") or "").strip()


def _load_schedule_monitor_state():
    path = schedule_monitor_file_for_user(DASHBOARD_USER_ID)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_schedule_monitor_state(state):
    path = schedule_monitor_file_for_user(DASHBOARD_USER_ID)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_schedule_changes(saa_snapshot):
    prev = _load_schedule_monitor_state()
    prev_rows = prev.get("rows") or []
    prev_ts = prev.get("updatedAt")

    now = get_now_iso()
    new_rows = []
    for item in saa_snapshot:
        new_rows.append(
            {
                "keyNoPob": _schedule_row_key_without_pob(item),
                "signature": _schedule_signature(item),
                "pob": str(item.get("pob") or "").strip(),
                "vesselName": item.get("vesselName") or "—",
                "berthName": item.get("berthName") or "—",
                "empRb": item.get("empRb") or "N/A",
            }
        )

    prev_sigs = {str(r.get("signature") or "") for r in prev_rows}
    new_sigs = {str(r.get("signature") or "") for r in new_rows}

    added = [r for r in new_rows if r["signature"] not in prev_sigs][:60]
    removed = [r for r in prev_rows if str(r.get("signature") or "") not in new_sigs][:60]

    prev_by_key = {}
    for r in prev_rows:
        k = str(r.get("keyNoPob") or "")
        if not k:
            continue
        prev_by_key.setdefault(k, []).append(r)
    new_by_key = {}
    for r in new_rows:
        k = r["keyNoPob"]
        new_by_key.setdefault(k, []).append(r)

    delayed = []
    advanced = []
    touched_keys = set(prev_by_key.keys()) & set(new_by_key.keys())
    for k in touched_keys:
        olds = sorted(prev_by_key[k], key=lambda x: str(x.get("pob") or ""))
        news = sorted(new_by_key[k], key=lambda x: str(x.get("pob") or ""))
        pairs = min(len(olds), len(news))
        for i in range(pairs):
            old_pob = str(olds[i].get("pob") or "")
            new_pob = str(news[i].get("pob") or "")
            if old_pob == new_pob:
                continue
            old_dt = _parse_pob_to_datetime(old_pob)
            new_dt = _parse_pob_to_datetime(new_pob)
            if not old_dt or not new_dt:
                continue
            delta_min = int(round((new_dt.timestamp() - old_dt.timestamp()) / 60.0))
            row = {
                "vesselName": news[i].get("vesselName") or "—",
                "berthName": news[i].get("berthName") or "—",
                "empRb": news[i].get("empRb") or "N/A",
                "oldPob": old_pob,
                "newPob": new_pob,
                "deltaMinutes": delta_min,
            }
            if delta_min > 0:
                delayed.append(row)
            elif delta_min < 0:
                advanced.append(row)

    changed = delayed[:40] + advanced[:40]
    summary = {
        "previousUpdatedAt": prev_ts,
        "currentUpdatedAt": now,
        "addedCount": len(added),
        "removedCount": len(removed),
        "delayedCount": len(delayed),
        "advancedCount": len(advanced),
        "anyChange": bool(added or removed or delayed or advanced),
        "added": added,
        "removed": removed,
        "delayed": delayed[:60],
        "advanced": advanced[:60],
        "changed": changed[:80],
    }

    _save_schedule_monitor_state({"updatedAt": now, "rows": new_rows})
    return summary


def _fetch_metocean_context():
    # Dados operacionais basicos para a baia de Guanabara (ponto medio)
    lat, lon = -22.90, -43.17
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=wind_speed_10m,wind_direction_10m"
        "&hourly=wind_speed_10m"
        "&timezone=America%2FSao_Paulo"
    )
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        cur = body.get("current") or {}
        return {
            "source": "open-meteo",
            "windSpeedKmh": cur.get("wind_speed_10m"),
            "windDirectionDeg": cur.get("wind_direction_10m"),
            "tide": "Integração de maré pendente (fonte local/hidrográfica).",
        }
    except Exception as exc:
        return {
            "source": "fallback",
            "windSpeedKmh": None,
            "windDirectionDeg": None,
            "tide": "Sem dados de maré online.",
            "error": str(exc),
        }


def _question_normalized(question: str) -> str:
    q = (question or "").strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", q) if unicodedata.category(c) != "Mn"
    )


def _question_asks_about_competitors(question: str) -> bool:
    q = _question_normalized(question)
    if not q:
        return False
    if "concorrent" in q or "competidor" in q or "rival" in q:
        return True
    if "quem sao" in q or "quem e " in q or "quem e o" in q:
        if "nosso" in q or "nossa" in q or "nos " in q or "empresa" in q:
            return True
    return False


def _competitor_fleet_catalog_text() -> str:
    lines = []
    for company in sorted(COMPETITOR_TUGS.keys()):
        bits = []
        for tug in COMPETITOR_TUGS[company]:
            label = (tug.get("name") or "").strip() or "—"
            mmsi = str(tug.get("mmsi") or "").strip()
            bits.append(f"{label} (MMSI {mmsi})" if mmsi else label)
        lines.append(f"- {company}: " + ", ".join(bits))
    return "\n".join(lines)


def _strategy_fallback_local_followup(question: str, context: dict) -> str:
    if not _question_asks_about_competitors(question):
        return ""
    comps = context.get("competitors") or []
    manobrando = [c for c in comps if c.get("insideManeuverGeofence")]
    lines_manobra = []
    for c in manobrando[:12]:
        nm = (c.get("name") or "—").strip()
        co = c.get("company") or "—"
        gf = (c.get("maneuverGeofenceName") or "—").strip()
        lines_manobra.append(f"  • {co} — {nm} (geofence: {gf})")
    manobra_txt = (
        "\nAgora em geofence de manobra (AIS):\n" + "\n".join(lines_manobra)
        if lines_manobra
        else "\nNeste momento nenhum rebocador concorrente da lista aparece com AIS dentro de geofence de manobra."
    )
    return (
        "\n\n---\n\n"
        "Resposta local (sem Grok)\n\n"
        "Os concorrentes que este dashboard acompanha por AIS são os rebocadores das empresas WIL e CAM "
        "(além da frota SAAM-BGRA, a vossa). Catálogo configurado:\n\n"
        f"{_competitor_fleet_catalog_text()}\n"
        "Na programação da Praticagem, o campo EMP.RB associa cada manobra a uma empresa (ex.: SAA, WIL, CAM); "
        "o resumo «Market share» no quadro acima conta quantas linhas na base existem por código EMP.RB.\n"
        f"{manobra_txt}"
    )


def _is_simple_greeting(question: str) -> bool:
    q = _question_normalized(question)
    if not q:
        return False
    for ch in "!?.,;:":
        q = q.replace(ch, " ")
    parts = [p for p in q.split() if p]
    if not parts:
        return False
    if len(parts) <= 2 and parts[0] in ("ola", "oi", "hi", "hello", "hey", "eai"):
        return True
    if (
        len(parts) >= 2
        and len(parts) <= 4
        and parts[0] in ("bom", "boa")
        and parts[1] in ("dia", "tarde", "noite")
    ):
        return True
    return False


def _strategy_context_dict():
    ensure_geofences_loaded()
    ensure_saa_maneuvers_loaded()
    with geofence_lock:
        geofence_snapshot = list(geofences)
    with saa_maneuvers_lock:
        saa_snapshot = _dedupe_saa_maneuvers(list(saa_maneuvers_list))
    saam_positions = []
    for mmsi in SAAM_BGRA_MMSI_SET:
        v = latest_vessel_by_mmsi.get(mmsi)
        if not v:
            continue
        saam_positions.append(
            {
                "mmsi": mmsi,
                "name": (v.get("shipName") or "").strip() or f"MMSI {mmsi}",
                "latitude": v.get("latitude"),
                "longitude": v.get("longitude"),
                "speed": v.get("speed"),
                "heading": v.get("heading"),
                "insideGeofences": get_vessel_geofences(v),
            }
        )
    upcoming = sorted(
        saa_snapshot,
        key=lambda x: str(x.get("pob") or ""),
    )[:40]
    competitors = _competitor_status_rows(geofence_snapshot)
    schedule_changes = _build_schedule_changes(saa_snapshot)
    memory_items = load_strategy_memory()
    return {
        "timestamp": get_now_iso(),
        "saamTugs": saam_positions,
        "scheduledManeuvers": upcoming,
        "scheduledManeuverTotal": len(saa_snapshot),
        "competitors": competitors,
        "marketShare": _market_share_rows(saa_snapshot),
        "simultaneousManeuvers": _simultaneous_maneuvers_summary(saa_snapshot),
        "scheduleChanges": schedule_changes,
        "metocean": _fetch_metocean_context(),
        "userLearnedNotes": memory_items[:30],
    }


def _strategy_fallback_answer(question: str, context: dict) -> str:
    saam = context.get("saamTugs") or []
    comps = context.get("competitors") or []
    maneuvers = context.get("scheduledManeuvers") or []
    m_total = int(context.get("scheduledManeuverTotal", len(maneuvers)))
    manobrando = [c for c in comps if c.get("insideManeuverGeofence")]
    top = (context.get("marketShare") or {}).get("rows") or []
    top_txt = ", ".join(f"{x['empRb']}: {x['count']}" for x in top[:4]) if top else "sem dados"
    intro = (
        "Olá. Bora olhar o cenário operacional agora (modo local, sem chamada ao Grok):\n\n"
        if _is_simple_greeting(question)
        else "Leitura rápida do cenário operacional (modo local, sem Grok):\n\n"
    )
    hint = (
        "Opcional: defina a variável de ambiente XAI_API_KEY (API xAI) para respostas com Grok "
        "usando este contexto — por exemplo num ficheiro `.env` na raiz do projeto ou nas variáveis do servidor."
    )
    follow = _strategy_fallback_local_followup(question, context)
    return (
        intro
        + f"Neste momento temos {len(saam)} rebocadores SAAM com posição AIS e {m_total} manobras na base da Praticagem.\n"
        + f"Concorrentes em geofence de manobra agora: {len(manobrando)}. Market share por EMP.RB (contagem): {top_txt}.\n"
        + f"Sobre a sua pergunta ('{question}'), com este recorte eu começaria por estes pontos práticos:\n"
        + "- priorizar janelas com sobreposição de manobras e necessidade de mais rebocadores;\n"
        + "- monitorar entradas simultâneas de concorrentes nas geofences críticas;\n"
        + "- revisar alocação com base no mix SAA/WIL/CAM do turno.\n"
        + follow
        + "\n\n"
        + hint
    )


def _assistant_profile_instruction() -> str:
    profile = ASSISTANT_PROFILE
    if profile == "executivo":
        return (
            "Perfil executivo: comece pelo impacto e recomendacao, use poucas frases e priorize decisao."
        )
    if profile == "operacional":
        return (
            "Perfil operacional de patio: detalhe janelas, geofences, alocacao e risco de conflito."
        )
    if profile == "despacho":
        return (
            "Perfil despacho: resposta curta, direta e orientada a acao imediata."
        )
    return (
        "Perfil hibrido: seja objetivo, mas inclua contexto essencial quando ajudar na decisao."
    )


def _ask_grok_with_context(question: str, context: dict) -> str:
    if not GROK_API_KEY:
        return _strategy_fallback_answer(question, context)
    payload = {
        "model": GROK_MODEL,
        "temperature": 0.45,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Voce e o KRATOS, assistente de estrategia naval do porto do Rio de Janeiro e "
                    "da Baia de Guanabara: experiente, consultivo e natural. Ao se apresentar, use o nome KRATOS. "
                    "Responda em portugues com linguagem clara, direta e mais solta (sem rigidez excessiva). "
                    "Baseie-se no contexto fornecido; se faltar dado, diga isso com transparencia. "
                    "Priorize insights acionaveis e recomendacoes praticas para operacao. "
                    + _assistant_profile_instruction()
                ),
            },
            {
                "role": "user",
                "content": (
                    "Contexto operacional JSON:\n"
                    + json.dumps(context, ensure_ascii=False)
                    + "\n\nPergunta:\n"
                    + question
                ),
            },
        ],
    }
    req = urllib.request.Request(
        url="https://api.x.ai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return (
            (((body.get("choices") or [{}])[0]).get("message") or {}).get("content")
            or "Sem resposta do Grok."
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return _strategy_fallback_answer(question, context) + f"\n\nErro Grok: {exc}"


def build_dashboard_overview_dict():
    ensure_live_worker_started()
    ensure_geofences_loaded()
    ensure_saa_maneuvers_loaded()
    with geofence_lock:
        gfs = list(geofences)
    with saam_geofence_stats_lock:
        tug_snapshot = json.loads(json.dumps(tug_stats_state))
    with saa_maneuvers_lock:
        saa_snapshot = _dedupe_saa_maneuvers(list(saa_maneuvers_list))
    chart = []
    by_m = tug_snapshot.get("byMmsi", {})
    for mmsi in SAAM_MMSI_ABBR:
        row = by_m.get(mmsi, {})
        chart.append(
            {
                "mmsi": mmsi,
                "abbr": row.get("abbr") or SAAM_MMSI_ABBR.get(mmsi, mmsi),
                "name": row.get("name", ""),
                "totalManeuvers": int(row.get("totalManeuvers", 0)),
                "totalHours": round(float(row.get("totalSeconds", 0)) / 3600.0, 2),
                "totalNauticalMiles": round(float(row.get("totalNauticalMiles", 0)), 2),
            }
        )
    market_share = _market_share_rows(saa_snapshot)
    market_share_windows = _market_share_windows(saa_snapshot)
    competitors = _competitor_status_rows(gfs)
    schedule_changes = _build_schedule_changes(saa_snapshot)
    return {
        "ok": True,
        "userId": DASHBOARD_USER_ID,
        "geofences": gfs,
        "geofenceStatus": _dashboard_geofence_status_rows(),
        "occupancy": build_geofence_occupancy(),
        "tugStats": tug_snapshot,
        "tugChart": chart,
        "saaManeuvers": saa_snapshot,
        "marketShare": market_share,
        "marketShareWindows": market_share_windows,
        "competitors": competitors,
        "scheduleChanges": schedule_changes,
    }


@app.get("/api/dashboard/overview")
def dashboard_overview():
    return build_dashboard_overview_dict()


@app.get("/dashboard/api/overview")
def dashboard_overview_under_dashboard_path():
    """Mesmo JSON que /api/dashboard/overview (registado antes das rotas /api/geofences/*)."""
    return build_dashboard_overview_dict()


@app.get("/api/dashboard/saa-maneuvers")
def get_saa_maneuvers():
    with saa_maneuvers_lock:
        return {"ok": True, "items": _dedupe_saa_maneuvers(list(saa_maneuvers_list))}


@app.post("/api/dashboard/saa-maneuvers")
async def append_saa_maneuver(request: Request):
    payload = await request.json()
    item = {
        "id": str(uuid.uuid4()),
        "vesselName": payload.get("vesselName", "").strip() or "—",
        "berthName": payload.get("berthName", "").strip() or "—",
        "empRb": (payload.get("empRb") or "SAA").strip(),
        "status": payload.get("status", "").strip() or "—",
        "note": (payload.get("note") or "").strip(),
        "recordedAt": get_now_iso(),
        **_saa_dims_from_payload(payload),
    }
    with saa_maneuvers_lock:
        saa_maneuvers_list.insert(0, item)
        save_saa_maneuvers()
    return {"ok": True, "item": item}


@app.post("/api/dashboard/strategy-assistant")
async def strategy_assistant(request: Request):
    payload = await request.json()
    question = str(payload.get("question") or "").strip()
    action = str(payload.get("action") or "ask").strip().lower()
    learn_note = str(payload.get("learnNote") or "").strip()
    if learn_note:
        append_strategy_memory(learn_note, author="user")
    if not question:
        return JSONResponse({"ok": False, "error": "question obrigatoria"}, status_code=400)
    context = _strategy_context_dict()
    if action == "report":
        question = (
            "Gere um relatorio executivo com: panorama operacional, market share (hoje/7d/30d), "
            "concorrentes manobrando, riscos meteoceanicos (vento/mare) e recomendacoes de alocacao. "
            + question
        )
    elif action == "insights":
        question = (
            "Gere insights acionaveis e hipoteses de ganho competitivo com base no contexto. "
            + question
        )
    answer = await asyncio.to_thread(_ask_grok_with_context, question, context)
    append_strategy_memory(f"Pergunta: {question}\nResposta: {answer[:1200]}", author="assistant")
    return {"ok": True, "answer": answer, "context": context}


@app.post("/dashboard/api/strategy-assistant")
async def strategy_assistant_under_dashboard_path(request: Request):
    """Mesmo comportamento de /api/dashboard/strategy-assistant para subpath /dashboard."""
    return await strategy_assistant(request)


@app.get("/api/geofences")
def get_geofences():
    ensure_geofences_loaded()
    with geofence_lock:
        return {"geofences": geofences}


@app.post("/api/geofences")
async def create_geofence(request: Request):
    payload = await request.json()
    geofence = {
        "id": str(uuid.uuid4()),
        "name": payload.get("name", "Novo geofence"),
        "type": payload.get("type", "berco"),
        "geometry": payload.get("geometry", {}),
        "fleetScope": payload.get("fleetScope", "all"),
        "isActive": bool(payload.get("isActive", True)),
        "color": payload.get("color", "#35c8ff"),
        "createdAt": get_now_iso(),
        "updatedAt": get_now_iso(),
    }
    with geofence_lock:
        geofences.append(geofence)
        save_geofences()
    return {"ok": True, "geofence": geofence}


@app.put("/api/geofences/{geofence_id}")
async def update_geofence(geofence_id: str, request: Request):
    payload = await request.json()
    with geofence_lock:
        for geofence in geofences:
            if geofence.get("id") == geofence_id:
                geofence["name"] = payload.get("name", geofence.get("name"))
                geofence["type"] = payload.get("type", geofence.get("type"))
                geofence["geometry"] = payload.get("geometry", geofence.get("geometry", {}))
                geofence["fleetScope"] = payload.get("fleetScope", geofence.get("fleetScope", "all"))
                geofence["isActive"] = bool(payload.get("isActive", geofence.get("isActive", True)))
                geofence["color"] = payload.get("color", geofence.get("color", "#35c8ff"))
                geofence["updatedAt"] = get_now_iso()
                save_geofences()
                return {"ok": True, "geofence": geofence}
    return {"ok": False, "error": "Geofence não encontrado"}


@app.delete("/api/geofences/{geofence_id}")
def delete_geofence(geofence_id: str):
    with geofence_lock:
        for g in geofences:
            if g.get("id") == geofence_id and _is_bg_interno_geofence(g):
                return {"ok": False, "error": "Geofence persistente nao pode ser apagado"}
        before = len(geofences)
        geofences[:] = [g for g in geofences if g.get("id") != geofence_id]
        if len(geofences) == before:
            return {"ok": False, "error": "Geofence não encontrado"}
        save_geofences()
    return {"ok": True}


@app.get("/api/geofences/occupancy")
def geofence_occupancy():
    return {"occupancy": build_geofence_occupancy()}


@app.get("/api/geofences/{geofence_id}/vessels")
def geofence_vessels(geofence_id: str):
    occupancy = build_geofence_occupancy()
    for item in occupancy:
        if item.get("geofenceId") == geofence_id:
            return {"ok": True, "vessels": item.get("insideVessels", []), "geofence": item}
    return {"ok": False, "error": "Geofence não encontrado"}


def _read_dashboard_html() -> str:
    path = FRONTEND_DIR / "dashboard.html"
    return path.read_text(encoding="utf-8")


def _json_for_inline_script(obj) -> str:
    """JSON seguro dentro de <script> (evita quebra por </script> ou < no payload)."""
    s = json.dumps(obj, ensure_ascii=False, default=str)
    return s.replace("<", "\\u003c")


def _dashboard_html_with_bootstrap() -> str:
    """Injeta window.__DASHBOARD_OVERVIEW__ para a página funcionar sem XHR a /api (ex.: proxy na 8080)."""
    html = _read_dashboard_html()
    try:
        payload = _json_for_inline_script(build_dashboard_overview_dict())
    except Exception:
        payload = _json_for_inline_script({"ok": False, "error": "Falha ao montar overview"})
    inject = f"<script>window.__DASHBOARD_OVERVIEW__={payload};</script>"
    if "</head>" in html:
        return html.replace("</head>", inject + "\n</head>", 1)
    return inject + html


@app.get("/dashboard")
def dashboard_page():
    """HTML com dados embutidos (bootstrap) + fallback por API no cliente."""
    return HTMLResponse(_dashboard_html_with_bootstrap())


@app.get("/dashboard/")
def dashboard_page_trailing_slash():
    return HTMLResponse(_dashboard_html_with_bootstrap())


@app.get("/dashboard.html")
def dashboard_page_html_file():
    """Alias com extensão (útil se o browser ou proxy esperar .html)."""
    return HTMLResponse(_dashboard_html_with_bootstrap())


@app.post("/api/mode")
async def set_mode(request: Request):
    global current_mode
    data = await request.json()
    if data.get("syncPraticagemSaa") in (True, 1, "1", "true"):
        return await _sync_saa_from_praticagem_impl()
    mode = data.get("mode", "live").lower()
    if mode != "live":
        return {"ok": False, "error": "Modo mock removido. Use apenas live."}
    if not AISSTREAM_API_KEY:
        return {"ok": False, "error": "AISSTREAM_API_KEY ausente no backend."}
    current_mode = "live"
    ensure_live_worker_started()
    return {"ok": True, "status": get_status()}

@app.post("/api/area")
async def set_area(request: Request):
    global current_area_key, last_subscription_update_monotonic
    data = await request.json()
    area = data.get("areaKey", "rio").lower()
    if area not in AREAS:
        return {"ok": False, "error": f"Área inválida: {area}"}
    if area == current_area_key:
        return {"ok": True, "status": get_status(), "updatedSubscription": False}

    if current_mode == "live":
        ensure_live_worker_started()
        now = time.monotonic()
        elapsed = now - last_subscription_update_monotonic
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
        last_subscription_update_monotonic = time.monotonic()

    current_area_key = area
    if current_mode == "live":
        live_subscription_update_event.set()
    return {"ok": True, "status": get_status(), "updatedSubscription": current_mode == "live"}

# --- WebSocket relay ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await relay_cached_stream(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "ais_error", "payload": {"error": str(e)}})

async def relay_cached_stream(websocket: WebSocket):
    """
    Relay para o frontend usando apenas o buffer local (`recent_vessels`).
    A conexão com AISStream fica centralizada no worker de background.
    """
    ensure_live_worker_started()
    last_sent_seq = 0
    if recent_vessels:
        last_sent_seq = recent_vessels[-1]["_seq"]
    await websocket.send_json({"type": "status", "payload": get_status()})
    next_status_at = time.monotonic() + 1.0

    while True:
        await asyncio.sleep(0.2)
        new_items = [v for v in recent_vessels if v.get("_seq", 0) > last_sent_seq]
        for vessel_payload in new_items:
            await websocket.send_json({"type": "ais", "payload": vessel_payload})
            last_sent_seq = vessel_payload.get("_seq", last_sent_seq)
        now = time.monotonic()
        if now >= next_status_at:
            await websocket.send_json({"type": "status", "payload": get_status()})
            next_status_at = now + 1.0

async def relay_live(websocket: WebSocket):
    global live_connected, last_error, last_ais_message_at, total_messages
    total_messages = 0
    backoff_seconds = 2

    while True:
        live_connected = False
        last_error = None
        try:
            async with websockets.connect(
                AISSTREAM_URL,
                ping_interval=30,
                ping_timeout=30,
            ) as ais_ws:
                live_subscription_update_event.clear()
                await ais_ws.send(json.dumps(build_live_subscription()))
                live_connected = True
                backoff_seconds = 2
                await websocket.send_json({"type": "status", "payload": get_status()})

                while True:
                    if live_subscription_update_event.is_set():
                        live_subscription_update_event.clear()
                        await ais_ws.send(json.dumps(build_live_subscription()))
                        await websocket.send_json({"type": "status", "payload": get_status()})
                        continue

                    try:
                        msg = await asyncio.wait_for(ais_ws.recv(), timeout=1.0)
                    except asyncio.TimeoutError:
                        continue
                    except ConnectionClosed as e:
                        last_error = f"Conexao AISStream encerrada: {e}"
                        live_connected = False
                        await websocket.send_json({"type": "status", "payload": get_status()})
                        break

                    try:
                        data = json.loads(msg)
                        if "error" in data:
                            last_error = data["error"]
                            await websocket.send_json({"type": "ais_error", "payload": data})
                            await websocket.send_json({"type": "status", "payload": get_status()})
                            continue
                        vessel = extract_normalized_vessel(data)
                        if vessel:
                            total_messages += 1
                            last_ais_message_at = vessel["payload"]["timestamp"]
                            push_recent_vessel(vessel["payload"])
                            await websocket.send_json(vessel)
                            await websocket.send_json({"type": "status", "payload": get_status()})
                    except Exception as e:
                        last_error = f"Falha ao ler mensagem do AISStream: {e}"
                        await websocket.send_json({"type": "status", "payload": get_status()})
        except WebSocketDisconnect:
            break
        except Exception as e:
            last_error = f"Erro no socket AISStream: {e}"
            live_connected = False
            try:
                await websocket.send_json({"type": "ais_error", "payload": {"error": last_error}})
                await websocket.send_json({"type": "status", "payload": get_status()})
            except Exception:
                break

            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 30)

    live_connected = False

async def live_background_worker():
    global live_connected, last_error, last_ais_message_at, total_messages
    backoff_seconds = 2
    while True:
        live_connected = False
        last_error = None
        try:
            async with websockets.connect(
                AISSTREAM_URL,
                ping_interval=30,
                ping_timeout=30,
            ) as ais_ws:
                live_subscription_update_event.clear()
                await ais_ws.send(json.dumps(build_live_subscription()))
                live_connected = True
                backoff_seconds = 2
                while True:
                    if live_subscription_update_event.is_set():
                        live_subscription_update_event.clear()
                        await ais_ws.send(json.dumps(build_live_subscription()))
                    try:
                        msg = await asyncio.wait_for(ais_ws.recv(), timeout=1.0)
                    except asyncio.TimeoutError:
                        continue
                    except ConnectionClosed as e:
                        last_error = f"Conexao AISStream encerrada: {e}"
                        live_connected = False
                        break
                    data = json.loads(msg)
                    if "error" in data:
                        last_error = data["error"]
                        continue
                    vessel = extract_normalized_vessel(data)
                    if vessel:
                        total_messages += 1
                        last_ais_message_at = vessel["payload"]["timestamp"]
                        push_recent_vessel(vessel["payload"])
        except Exception as e:
            last_error = f"Erro no socket AISStream: {e}"
            live_connected = False
        await asyncio.sleep(backoff_seconds)
        backoff_seconds = min(backoff_seconds * 2, 30)

async def relay_mock(websocket: WebSocket):
    global total_messages, last_ais_message_at, live_connected
    live_connected = False
    while True:
        vessels = generate_mock_vessels(current_area_key)
        for vessel in vessels:
            print(f"[MOCK] Enviando alvo simulado: {vessel}")
            await websocket.send_json({"type": "ais", "payload": vessel})
            total_messages += 1
            last_ais_message_at = vessel["timestamp"]
        print("[MOCK] Status enviado para frontend.")
        await websocket.send_json({"type": "status", "payload": get_status()})
        await asyncio.sleep(2)

def extract_normalized_vessel(data):
    try:
        metadata = data.get("MetaData") or data.get("Metadata") or {}
        message_type = data.get("MessageType", "Unknown")
        message_wrapper = data.get("Message", {})
        message_body = message_wrapper.get(message_type) or next(iter(message_wrapper.values()), {})
        mmsi = str(metadata.get("MMSI") or message_body.get("UserID") or "desconhecido")
        cached = vessel_state_by_mmsi.get(mmsi, {})
        latitude = (
            metadata.get("latitude") or metadata.get("Latitude") or message_body.get("Latitude") or message_body.get("latitude")
        )
        longitude = (
            metadata.get("longitude") or metadata.get("Longitude") or message_body.get("Longitude") or message_body.get("longitude")
        )
        if latitude is None or longitude is None:
            return None
        incoming_name = metadata.get("ShipName") or message_body.get("Name")
        ship_name = incoming_name or cached.get("shipName") or "Sem nome"
        incoming_ship_type_code = normalize_ship_type_code(metadata, message_body)
        ship_type_code = incoming_ship_type_code if incoming_ship_type_code is not None else cached.get("shipTypeCode")
        is_saam_bgra = mmsi in SAAM_BGRA_MMSI_SET
        ship_category = "rebocador_servico" if is_saam_bgra else infer_ship_category(ship_type_code, ship_name)
        latitude_f = float(latitude)
        longitude_f = float(longitude)
        fallback_geofence = classify_geofence(latitude_f, longitude_f)

        ais_length_m, ais_beam_m = extract_ship_dimensions_meters(message_type, message_body)
        cached_ais_length = cached.get("lengthMetersAis")
        cached_ais_beam = cached.get("beamMetersAis")

        if ais_length_m is not None:
            length_source = "ais_dimension"
            length_m = ais_length_m
            beam_m = ais_beam_m if ais_beam_m is not None else cached_ais_beam
        elif cached_ais_length is not None:
            length_source = "ais_dimension_cached"
            length_m = float(cached_ais_length)
            beam_m = cached_ais_beam
        else:
            length_source = "estimated_category"
            length_m = estimate_length_from_category(ship_category)
            beam_m = None

        vessel_state_by_mmsi[mmsi] = {
            "shipName": ship_name,
            "shipTypeCode": ship_type_code,
            "shipCategory": ship_category,
            "fleet": SAAM_BGRA_FLEET_NAME if is_saam_bgra else None,
            "lengthMetersAis": ais_length_m if ais_length_m is not None else cached_ais_length,
            "beamMetersAis": ais_beam_m if ais_beam_m is not None else cached_ais_beam,
        }
        vessel_data = {
            "source": current_mode,
            "messageType": message_type,
            "mmsi": mmsi,
            "shipName": ship_name,
            "shipTypeCode": ship_type_code,
            "shipCategory": ship_category,
            "fleet": SAAM_BGRA_FLEET_NAME if is_saam_bgra else None,
            "isSaamBgra": is_saam_bgra,
            "geofence": fallback_geofence,
            "latitude": latitude_f,
            "longitude": longitude_f,
            "sog": float(message_body.get("Sog") or message_body.get("SpeedOverGround") or 0),
            "cog": float(message_body.get("Cog") or message_body.get("CourseOverGround") or 0),
            "heading": float(message_body.get("TrueHeading") or message_body.get("Heading") or 0),
            "navStatus": message_body.get("NavigationalStatus"),
            "lengthMeters": length_m,
            "beamMeters": beam_m,
            "lengthSource": length_source,
            "timestamp": metadata.get("time_utc") or metadata.get("timeUTC") or get_now_iso(),
            "raw": data
        }
        vessel_data["geofencesInside"] = get_vessel_geofences(vessel_data)
        vessel_data["inRebocadorBase"] = vessel_in_rebocador_base(vessel_data)
        if vessel_data["geofencesInside"] and not vessel_data.get("geofence"):
            vessel_data["geofence"] = vessel_data["geofencesInside"][0]
        latest_vessel_by_mmsi[mmsi] = vessel_data
        update_saam_nautical_miles(vessel_data)
        update_saam_fleet_geofence_stats(vessel_data)

        return {
            "type": "ais",
            "payload": vessel_data
        }
    except Exception:
        return None

def get_now_iso():
    return datetime.utcnow().isoformat()

def generate_mock_vessels(area_key):
    presets = {
        "suape": [
            {"mmsi": "710000101", "shipName": "TUG SUAPE ALFA", "shipTypeCode": 52, "latitude": -8.403, "longitude": -34.969, "sog": 8.2, "cog": 112, "lengthMeters": 32, "beamMeters": 11, "lengthSource": "mock"},
            {"mmsi": "710000102", "shipName": "NAVIO RECIFE STAR", "shipTypeCode": 70, "latitude": -8.377, "longitude": -34.912, "sog": 11.4, "cog": 221, "lengthMeters": 190, "beamMeters": 28, "lengthSource": "mock"}
        ],
        "santos": [
            {"mmsi": "710000201", "shipName": "TUG SANTOS BRAVO", "shipTypeCode": 52, "latitude": -23.992, "longitude": -46.307, "sog": 7.1, "cog": 41, "lengthMeters": 30, "beamMeters": 10, "lengthSource": "mock"},
            {"mmsi": "710000202", "shipName": "CARGUEIRO ATLANTICO SUL", "shipTypeCode": 70, "latitude": -24.038, "longitude": -46.283, "sog": 9.8, "cog": 78, "lengthMeters": 210, "beamMeters": 32, "lengthSource": "mock"}
        ],
        "rio": [
            {"mmsi": "710000301", "shipName": "TUG GUANABARA", "shipTypeCode": 52, "latitude": -22.882, "longitude": -43.146, "sog": 6.8, "cog": 132, "lengthMeters": 28, "beamMeters": 9, "lengthSource": "mock"},
            {"mmsi": "710000302", "shipName": "RIO BAY TRADER", "shipTypeCode": 70, "latitude": -22.930, "longitude": -43.180, "sog": 10.6, "cog": 212, "lengthMeters": 200, "beamMeters": 30, "lengthSource": "mock"}
        ],
        "paranagua": [
            {"mmsi": "710000401", "shipName": "TUG PARANAGUA DELTA", "shipTypeCode": 52, "latitude": -25.522, "longitude": -48.501, "sog": 5.2, "cog": 94, "lengthMeters": 29, "beamMeters": 10, "lengthSource": "mock"},
            {"mmsi": "710000402", "shipName": "PR PORT CONTAINER", "shipTypeCode": 70, "latitude": -25.565, "longitude": -48.472, "sog": 8.7, "cog": 176, "lengthMeters": 205, "beamMeters": 31, "lengthSource": "mock"}
        ],
        "bahia": [
            {"mmsi": "710000501", "shipName": "TUG TODOS OS SANTOS", "shipTypeCode": 52, "latitude": -12.915, "longitude": -38.661, "sog": 4.7, "cog": 63, "lengthMeters": 27, "beamMeters": 9, "lengthSource": "mock"},
            {"mmsi": "710000502", "shipName": "BAHIA MINERAL", "shipTypeCode": 80, "latitude": -12.806, "longitude": -38.485, "sog": 12.0, "cog": 149, "lengthMeters": 240, "beamMeters": 40, "lengthSource": "mock"}
        ],
        "brasil_sudeste": [
            {"mmsi": "710000601", "shipName": "COSTA SUDESTE 01", "shipTypeCode": 70, "latitude": -23.300, "longitude": -42.500, "sog": 13.6, "cog": 205, "lengthMeters": 215, "beamMeters": 33, "lengthSource": "mock"},
            {"mmsi": "710000602", "shipName": "COSTA SUDESTE 02", "shipTypeCode": 60, "latitude": -24.200, "longitude": -44.100, "sog": 12.9, "cog": 35, "lengthMeters": 160, "beamMeters": 26, "lengthSource": "mock"}
        ]
    }
    from datetime import datetime
    drift = ((datetime.utcnow().timestamp() % 10) / 10000)
    vessels = presets.get(area_key, presets["suape"])
    for i, vessel in enumerate(vessels):
        vessel = vessel.copy()
        vessel["latitude"] += drift * (1 if i == 0 else -1)
        vessel["longitude"] += drift * (-1 if i == 0 else 1)
        vessel["heading"] = vessel["cog"]
        vessel["navStatus"] = 0
        vessel["shipCategory"] = infer_ship_category(vessel.get("shipTypeCode"), vessel.get("shipName"))
        vessel["timestamp"] = get_now_iso()
        yield vessel


async def _praticagem_auto_sync_loop():
    sec = int(os.getenv("PRATICAGEM_AUTO_SYNC_SECONDS", "60") or "60")
    if sec <= 0:
        return
    await asyncio.sleep(10)
    while True:
        try:
            await _sync_saa_from_praticagem_impl()
        except asyncio.CancelledError:
            break
        except Exception:
            pass
        try:
            await asyncio.sleep(sec)
        except asyncio.CancelledError:
            break


@app.on_event("startup")
async def startup_event():
    global live_worker_task, _praticagem_auto_sync_task
    load_geofences()
    load_tug_stats()
    load_saa_maneuvers()
    if current_mode == "live" and AISSTREAM_API_KEY and live_worker_task is None:
        live_worker_task = asyncio.create_task(live_background_worker())
    if int(os.getenv("PRATICAGEM_AUTO_SYNC_SECONDS", "60") or "60") > 0:
        _praticagem_auto_sync_task = asyncio.create_task(_praticagem_auto_sync_loop())


@app.on_event("shutdown")
async def shutdown_event():
    global live_worker_task, _praticagem_auto_sync_task
    try:
        save_tug_stats()
    except Exception:
        pass
    if _praticagem_auto_sync_task:
        _praticagem_auto_sync_task.cancel()
        try:
            await _praticagem_auto_sync_task
        except (asyncio.CancelledError, Exception):
            pass
        _praticagem_auto_sync_task = None
    if live_worker_task:
        live_worker_task.cancel()
        live_worker_task = None


@app.get("/frontend/dashboard.html")
def redirect_frontend_dashboard_to_canonical():
    """Ficheiro estático não inclui dados embutidos; força a rota /dashboard."""
    return RedirectResponse(url="/dashboard", status_code=307)


app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=False,
    )
