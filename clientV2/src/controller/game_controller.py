import asyncio
import threading
import socketio
from PySide6.QtCore import QObject, Signal
import os
import sys

# Ajout du dossier root au path pour accéder à src.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.core import cli_conf


# Helper pour émettre des signaux depuis le thread asyncio vers Qt
class NetworkSignals(QObject):
    connected = Signal()
    lobby_updated = Signal(list)


class GameController:
    def __init__(self):
        self.view = None
        self.sio = socketio.AsyncClient()
        self.signals = NetworkSignals()
        self.loop = asyncio.new_event_loop()

        # Signaux pour la mise à jour UI
        self.signals.connected.connect(self._on_connection_success)
        self.signals.lobby_updated.connect(self._on_lobby_updated)

        # Lancement de la boucle asyncio dans un thread séparé
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

        # Enregistrement des événements SIO
        self._setup_sio_events()

    def _setup_sio_events(self):
        @self.sio.on('lobby_list')
        async def on_lobby_list(data):
            self.signals.lobby_updated.emit(data)

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def set_view(self, view):
        self.view = view

    def connect_to_server(self, username):
        """Appelé par la vue pour initier la connexion"""
        url = f"http://{cli_conf.SERV_IP}:{cli_conf.SERV_PORT}"
        print(f"Tentative de connexion à {url} pour {username}...")

        asyncio.run_coroutine_threadsafe(self._async_connect(url, username), self.loop)

    async def _async_connect(self, url, username):
        try:
            await self.sio.connect(url, auth={'username': username})
            print("Connecté au serveur !")
            self.signals.connected.emit()
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def create_lobby(self):
        asyncio.run_coroutine_threadsafe(self._async_create(), self.loop)

    async def _async_create(self):
        res = await self.sio.call('create_lobby', {})
        print(f"Lobby créé: {res}")

    def join_lobby(self, lobby_id):
        asyncio.run_coroutine_threadsafe(self._async_join(lobby_id), self.loop)

    async def _async_join(self, lobby_id):
        res = await self.sio.call('join_lobby', {'lobby_id': lobby_id})
        print(f"Joint: {res}")

    # --- Callbacks UI (exécutés dans le thread principal) ---
    def _on_connection_success(self):
        if self.view:
            self.view.show_lobby_list_view()

    def _on_lobby_updated(self, lobbies):
        if self.view:
            self.view.lobby_view.update_lobbies(lobbies)