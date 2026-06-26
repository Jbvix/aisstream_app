"""
passenger_wsgi.py — entrada para cPanel + Phusion Passenger.

Passenger fala WSGI; FastAPI é ASGI. a2wsgi faz a ponte.
ATENÇÃO: WSGI não suporta WebSocket — se o app usar streaming em tempo real,
use polling em produção (ver ADR de polling no projeto KRATOS original).

O app fica montado sob um subcaminho (ex.: /meuapp). O Passenger envia
SCRIPT_NAME; o FastAPI lê via root_path para acertar redirects/cookies.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware  # noqa: E402
from main import app  # noqa: E402

# Passenger preenche SCRIPT_NAME por requisição; a2wsgi repassa como root_path.
application = ASGIMiddleware(app)
