import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import asyncio
import json
import websockets
import time
import threading
from collections import deque
from websockets.exceptions import ConnectionClosed

load_dotenv()

PORT = int(os.getenv("PORT", 8080))
AIS_MODE = os.getenv("AIS_MODE", "mock").lower()
AISSTREAM_API_KEY = os.getenv("AISSTREAM_API_KEY", "")
DEFAULT_AREA = os.getenv("DEFAULT_AREA", "suape").lower()
AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream"

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
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def root():
    return FileResponse("frontend/index.html", media_type="text/html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_area_key = DEFAULT_AREA if DEFAULT_AREA in AREAS else "suape"
current_mode = "live"
live_connected = False
last_error = None
last_ais_message_at = None
total_messages = 0
live_subscription_update_event = asyncio.Event()
last_subscription_update_monotonic = 0.0
vessel_state_by_mmsi = {}
recent_vessels = deque(maxlen=4000)
last_vessel_seq = 0
live_worker_task = None
live_worker_thread = None
live_worker_lock = threading.Lock()


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
    raw_type = (
        metadata.get("ShipType")
        or metadata.get("ship_type")
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
    if "TUG" in name or "REBOC" in name:
        return "rebocador_servico"
    if "TANK" in name or "PETRO" in name:
        return "petroleiro"
    if "CARGO" in name or "BULK" in name or "CONTAINER" in name:
        return "carga"
    if "FISH" in name or "PESCA" in name:
        return "pesca"
    if "PASSENGER" in name or "FERRY" in name:
        return "passageiros"
    return "outros"


def push_recent_vessel(vessel_payload):
    global last_vessel_seq
    last_vessel_seq += 1
    item = dict(vessel_payload)
    item["_seq"] = last_vessel_seq
    recent_vessels.append(item)


# --- REST endpoints ---
@app.get("/api/status")
def get_status():
    ensure_live_worker_started()
    return {
        "app": "AISStream Brasil App",
        "version": "1.0.0",
        "mode": current_mode,
        "area": AREAS.get(current_area_key, {}),
        "areaKey": current_area_key,
        "liveConnected": live_connected,
        "lastError": last_error,
        "lastAisMessageAt": last_ais_message_at,
        "totalMessages": total_messages
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/api/areas")
def get_areas():
    ensure_live_worker_started()
    return {"areas": AREAS, "currentAreaKey": current_area_key}

@app.get("/api/vessels")
def get_vessels(since: int = 0, limit: int = 300):
    ensure_live_worker_started()
    items = [v for v in recent_vessels if v.get("_seq", 0) > since]
    if limit > 0:
        items = items[-limit:]
    current_seq = recent_vessels[-1]["_seq"] if recent_vessels else since
    return {
        "vessels": items,
        "lastSeq": current_seq,
        "count": len(items)
    }

@app.post("/api/mode")
async def set_mode(request: Request):
    global current_mode
    data = await request.json()
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
    area = data.get("areaKey", "suape").lower()
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
        await relay_live(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "ais_error", "payload": {"error": str(e)}})

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
        ship_category = infer_ship_category(ship_type_code, ship_name)

        vessel_state_by_mmsi[mmsi] = {
            "shipName": ship_name,
            "shipTypeCode": ship_type_code,
            "shipCategory": ship_category,
        }

        return {
            "type": "ais",
            "payload": {
                "source": current_mode,
                "messageType": message_type,
                "mmsi": mmsi,
                "shipName": ship_name,
                "shipTypeCode": ship_type_code,
                "shipCategory": ship_category,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "sog": float(message_body.get("Sog") or message_body.get("SpeedOverGround") or 0),
                "cog": float(message_body.get("Cog") or message_body.get("CourseOverGround") or 0),
                "heading": float(message_body.get("TrueHeading") or message_body.get("Heading") or 0),
                "navStatus": message_body.get("NavigationalStatus"),
                "timestamp": metadata.get("time_utc") or metadata.get("timeUTC") or get_now_iso(),
                "raw": data
            }
        }
    except Exception:
        return None

def get_now_iso():
    from datetime import datetime
    return datetime.utcnow().isoformat()

def generate_mock_vessels(area_key):
    presets = {
        "suape": [
            {"mmsi": "710000101", "shipName": "TUG SUAPE ALFA", "shipTypeCode": 52, "latitude": -8.403, "longitude": -34.969, "sog": 8.2, "cog": 112},
            {"mmsi": "710000102", "shipName": "NAVIO RECIFE STAR", "shipTypeCode": 70, "latitude": -8.377, "longitude": -34.912, "sog": 11.4, "cog": 221}
        ],
        "santos": [
            {"mmsi": "710000201", "shipName": "TUG SANTOS BRAVO", "shipTypeCode": 52, "latitude": -23.992, "longitude": -46.307, "sog": 7.1, "cog": 41},
            {"mmsi": "710000202", "shipName": "CARGUEIRO ATLANTICO SUL", "shipTypeCode": 70, "latitude": -24.038, "longitude": -46.283, "sog": 9.8, "cog": 78}
        ],
        "rio": [
            {"mmsi": "710000301", "shipName": "TUG GUANABARA", "shipTypeCode": 52, "latitude": -22.882, "longitude": -43.146, "sog": 6.8, "cog": 132},
            {"mmsi": "710000302", "shipName": "RIO BAY TRADER", "shipTypeCode": 70, "latitude": -22.930, "longitude": -43.180, "sog": 10.6, "cog": 212}
        ],
        "paranagua": [
            {"mmsi": "710000401", "shipName": "TUG PARANAGUA DELTA", "shipTypeCode": 52, "latitude": -25.522, "longitude": -48.501, "sog": 5.2, "cog": 94},
            {"mmsi": "710000402", "shipName": "PR PORT CONTAINER", "shipTypeCode": 70, "latitude": -25.565, "longitude": -48.472, "sog": 8.7, "cog": 176}
        ],
        "bahia": [
            {"mmsi": "710000501", "shipName": "TUG TODOS OS SANTOS", "shipTypeCode": 52, "latitude": -12.915, "longitude": -38.661, "sog": 4.7, "cog": 63},
            {"mmsi": "710000502", "shipName": "BAHIA MINERAL", "shipTypeCode": 80, "latitude": -12.806, "longitude": -38.485, "sog": 12.0, "cog": 149}
        ],
        "brasil_sudeste": [
            {"mmsi": "710000601", "shipName": "COSTA SUDESTE 01", "shipTypeCode": 70, "latitude": -23.300, "longitude": -42.500, "sog": 13.6, "cog": 205},
            {"mmsi": "710000602", "shipName": "COSTA SUDESTE 02", "shipTypeCode": 60, "latitude": -24.200, "longitude": -44.100, "sog": 12.9, "cog": 35}
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


@app.on_event("startup")
async def startup_event():
    global live_worker_task
    if current_mode == "live" and AISSTREAM_API_KEY and live_worker_task is None:
        live_worker_task = asyncio.create_task(live_background_worker())


@app.on_event("shutdown")
async def shutdown_event():
    global live_worker_task
    if live_worker_task:
        live_worker_task.cancel()
        live_worker_task = None
