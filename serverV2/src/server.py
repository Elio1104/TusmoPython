"""
Point d'entrée ASGI du serveur Tusmo V2.
Instancie le LobbyManager, charge le dictionnaire, enregistre les handlers.
"""
import sys
import os
from pathlib import Path

import socketio

# Résolution des imports depuis la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.conf import SERV_IP, SERV_PORT, ACTIVE_DICT
from src.core.logic import load_dictionary
from src.manager.lobby_manager import LobbyManager
from src.events.handlers import register_handlers

# --- Chargement du dictionnaire ---
DICT_PATH = Path(__file__).parent.parent.parent / "core" / ACTIVE_DICT
dictionary = load_dictionary(str(DICT_PATH))

if not dictionary:
    print("[WARN] Dictionnaire vide, utilisation d'une liste de secours.")
    dictionary = ["TUSMO", "PYTHON", "SOCKET", "SERVEUR", "CLIENT", "LEAGUE", "YASUO"]

# --- Initialisation Socket.IO ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)

# --- Initialisation du manager ---
manager = LobbyManager(dictionary)

# --- Enregistrement des événements ---
register_handlers(sio, manager)
