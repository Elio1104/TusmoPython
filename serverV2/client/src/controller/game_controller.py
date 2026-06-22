import asyncio
import threading
import socketio
from PySide6.QtCore import QObject, Signal
from core.cli_conf import SERV_IP, SERV_PORT


class NetworkSignals(QObject):
    connected          = Signal()
    disconnected       = Signal()
    lobby_list_updated = Signal(list)
    lobby_updated      = Signal(dict)
    game_started       = Signal(dict)
    game_over          = Signal(dict)   # résultat personnel (has_won, word)
    game_finished      = Signal(dict)   # fin globale (word, scores)
    lobby_reset        = Signal(dict)   # lobby remis en attente
    player_guessed     = Signal(dict)   # un joueur a soumis un guess
    error_received     = Signal(str, str)


class GameController:
    def __init__(self):
        self.view          = None
        self.username      = None
        self.current_lobby = None
        self._last_has_won = False

        self.sio     = socketio.AsyncClient()
        self.signals = NetworkSignals()
        self.loop    = asyncio.new_event_loop()

        self.signals.connected.connect(self._on_connected)
        self.signals.lobby_list_updated.connect(self._on_lobby_list_updated)
        self.signals.lobby_updated.connect(self._on_lobby_updated)
        self.signals.game_started.connect(self._on_game_started)
        self.signals.game_over.connect(self._on_game_over)
        self.signals.game_finished.connect(self._on_game_finished)
        self.signals.lobby_reset.connect(self._on_lobby_reset)
        self.signals.player_guessed.connect(self._on_player_guessed)
        self.signals.error_received.connect(self._on_error_received)

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self._setup_events()

    # ------------------------------------------------------------------ #
    #  Setup événements SIO                                                #
    # ------------------------------------------------------------------ #

    def _setup_events(self):
        @self.sio.on("lobby_list")
        async def on_lobby_list(data):
            self.signals.lobby_list_updated.emit(data)

        @self.sio.on("lobby_update")
        async def on_lobby_update(data):
            self.current_lobby = data
            self.signals.lobby_updated.emit(data)

        @self.sio.on("game_started")
        async def on_game_started(data):
            self.signals.game_started.emit(data)

        @self.sio.on("game_over")
        async def on_game_over(data):
            self._last_has_won = data.get("has_won", False)
            self.signals.game_over.emit(data)

        @self.sio.on("game_finished")
        async def on_game_finished(data):
            self.signals.game_finished.emit(data)

        @self.sio.on("lobby_reset")
        async def on_lobby_reset(data):
            self.current_lobby = data
            self.signals.lobby_reset.emit(data)

        @self.sio.on("player_guessed")
        async def on_player_guessed(data):
            self.signals.player_guessed.emit(data)

        @self.sio.on("disconnect")
        async def on_disconnect():
            self.signals.disconnected.emit()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def set_view(self, view):
        self.view = view

    @property
    def my_sid(self) -> str:
        """Retourne le SID de ce client (vide si non connecté)."""
        try:
            return self.sio.get_sid() or ""
        except Exception:
            return ""

    # ------------------------------------------------------------------ #
    #  Actions publiques                                                   #
    # ------------------------------------------------------------------ #

    def connect_to_server(self, username: str):
        self.username = username
        url = f"http://{SERV_IP}:{SERV_PORT}"
        asyncio.run_coroutine_threadsafe(self._async_connect(url, username), self.loop)

    def create_lobby(self):
        asyncio.run_coroutine_threadsafe(self._async_create_lobby(), self.loop)

    def join_lobby(self, lobby_id: str):
        asyncio.run_coroutine_threadsafe(self._async_join_lobby(lobby_id), self.loop)

    def leave_lobby(self):
        asyncio.run_coroutine_threadsafe(self._async_leave_lobby(), self.loop)

    def set_ready(self, ready: bool = True):
        asyncio.run_coroutine_threadsafe(self._async_ready(ready), self.loop)

    def start_game(self):
        asyncio.run_coroutine_threadsafe(self._async_start_game(), self.loop)

    def send_guess(self, guess: str):
        asyncio.run_coroutine_threadsafe(self._async_send_guess(guess), self.loop)

    def replay(self):
        asyncio.run_coroutine_threadsafe(self._async_replay(), self.loop)

    # ------------------------------------------------------------------ #
    #  Coroutines async                                                    #
    # ------------------------------------------------------------------ #

    async def _async_connect(self, url: str, username: str):
        try:
            await self.sio.connect(url, auth={"username": username})
            self.signals.connected.emit()
        except Exception as e:
            self.signals.error_received.emit("CONNECTION_ERROR", str(e))

    async def _async_create_lobby(self):
        res = await self.sio.call("create_lobby", {"username": self.username})
        if res and res.get("success"):
            self.current_lobby = res.get("lobby")
        else:
            self._emit_error(res)

    async def _async_join_lobby(self, lobby_id: str):
        res = await self.sio.call("join_lobby", {"lobby_id": lobby_id, "username": self.username})
        if res and res.get("success"):
            self.current_lobby = res.get("lobby")
        else:
            self._emit_error(res)

    async def _async_leave_lobby(self):
        res = await self.sio.call("leave_lobby", {})
        if res and res.get("success"):
            self.current_lobby = None
        else:
            self._emit_error(res)

    async def _async_ready(self, ready: bool):
        await self.sio.call("ready_lobby", {"ready": ready})

    async def _async_start_game(self):
        res = await self.sio.call("start_lobby", {})
        if not res or not res.get("success"):
            self._emit_error(res)

    async def _async_send_guess(self, guess: str):
        res = await self.sio.call("send_guess", {"guess": guess})
        if res and not res.get("success"):
            self._emit_error(res)

    async def _async_replay(self):
        res = await self.sio.call("replay", {})
        if not res or not res.get("success"):
            self._emit_error(res)

    def _emit_error(self, res):
        if res:
            self.signals.error_received.emit(res.get("error", "UNKNOWN"), res.get("message", ""))
        else:
            self.signals.error_received.emit("NO_RESPONSE", "")

    # ------------------------------------------------------------------ #
    #  Callbacks UI (thread principal Qt)                                  #
    # ------------------------------------------------------------------ #

    def _on_connected(self):
        if self.view:
            self.view.show_lobby_list_view()

    def _on_lobby_list_updated(self, lobbies: list):
        if self.view:
            self.view.lobby_list_view.update_lobbies(lobbies)

    def _on_lobby_updated(self, lobby: dict):
        if self.view:
            self.view.lobby_room_view.update_lobby(lobby)
            self.view.show_lobby_room_view()

    def _on_game_started(self, data: dict):
        if self.view:
            self.view.show_game_view(data)

    def _on_game_over(self, data: dict):
        # Stocké pour l'affichage final — game_finished arrive juste après
        self._last_has_won = data.get("has_won", False)

    def _on_game_finished(self, data: dict):
        if self.view:
            word   = data.get("word", "")
            scores = data.get("scores", [])
            self.view.show_end_game_view(word, scores, self._last_has_won)

    def _on_lobby_reset(self, lobby: dict):
        if self.view:
            self.view.lobby_room_view.update_lobby(lobby)
            self.view.show_lobby_room_view()

    def _on_player_guessed(self, data: dict):
        """Affiche le résultat d'un autre joueur dans la game_view (optionnel)."""
        if self.view and hasattr(self.view.game_view, "display_guess_result"):
            # On n'affiche que son propre résultat via send_guess ACK
            pass

    def _on_error_received(self, error_code: str, message: str):
        print(f"[ERR] {error_code}: {message}")
        if self.view:
            self.view.show_error(error_code, message)
