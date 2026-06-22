"""
Enregistrement de tous les événements Socket.IO.
Appelé une seule fois depuis server.py avec register_handlers(sio, manager).
"""
import socketio
from src.manager.lobby_manager import LobbyManager
from src.core.constants import ErrorCodes


def register_handlers(sio: socketio.AsyncServer, manager: LobbyManager):

    # ------------------------------------------------------------------ #
    #  Connexion / Déconnexion                                             #
    # ------------------------------------------------------------------ #

    @sio.event
    async def connect(sid, environ, auth):
        username = (auth or {}).get("username", f"Player_{sid[:4]}")
        sio.enter_room(sid, "lobby_browsing")
        print(f"[CONNECT] {username} ({sid})")
        await sio.emit("lobby_list", manager.serialize_lobbies(), to=sid)

    @sio.event
    async def disconnect(sid):
        lobby = manager.get_player_lobby(sid)
        if lobby:
            lobby_id = lobby.id
            updated  = manager.leave_lobby(sid)
            if updated:
                await sio.emit("lobby_update", manager.serialize_lobby(lobby_id), room=lobby_id)
            await _broadcast_lobbies()
        print(f"[DISCONNECT] {sid}")

    # ------------------------------------------------------------------ #
    #  Gestion des lobbies                                                 #
    # ------------------------------------------------------------------ #

    @sio.on("create_lobby")
    async def create_lobby(sid, data):
        username = (data or {}).get("username", f"Player_{sid[:4]}")
        try:
            lobby = manager.create_lobby(sid, username)
            sio.leave_room(sid, "lobby_browsing")
            sio.enter_room(sid, lobby.id)
            await _broadcast_lobbies()
            return {"success": True, "lobby": manager.serialize_lobby(lobby.id)}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @sio.on("join_lobby")
    async def join_lobby(sid, data):
        lobby_id = (data or {}).get("lobby_id", "")
        username = (data or {}).get("username", f"Player_{sid[:4]}")
        try:
            lobby = manager.join_lobby(sid, username, lobby_id)
            sio.leave_room(sid, "lobby_browsing")
            sio.enter_room(sid, lobby.id)
            await sio.emit("lobby_update", manager.serialize_lobby(lobby.id), room=lobby.id)
            await _broadcast_lobbies()
            return {"success": True, "lobby": manager.serialize_lobby(lobby.id)}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    @sio.on("leave_lobby")
    async def leave_lobby(sid, data):
        lobby = manager.get_player_lobby(sid)
        if not lobby:
            return {"success": False, "error": ErrorCodes.NOT_IN_LOBBY}

        lobby_id = lobby.id
        updated  = manager.leave_lobby(sid)
        sio.leave_room(sid, lobby_id)
        sio.enter_room(sid, "lobby_browsing")

        if updated:
            await sio.emit("lobby_update", manager.serialize_lobby(lobby_id), room=lobby_id)
        await _broadcast_lobbies()
        return {"success": True}

    @sio.on("ready_lobby")
    async def ready_lobby(sid, data):
        ready = (data or {}).get("ready", True)
        lobby = manager.set_ready(sid, ready)
        if not lobby:
            return {"success": False, "error": ErrorCodes.NOT_IN_LOBBY}
        await sio.emit("lobby_update", manager.serialize_lobby(lobby.id), room=lobby.id)
        return {"success": True}

    @sio.on("start_lobby")
    async def start_lobby(sid, data):
        try:
            lobby = manager.start_game(sid)
        except ValueError as e:
            return {"success": False, "error": str(e)}

        game_info = {
            "word_length": len(lobby.game_state.word),
            "first_char":  lobby.game_state.word[0],
        }
        await sio.emit("game_started", game_info, room=lobby.id)
        await sio.emit("lobby_update", manager.serialize_lobby(lobby.id), room=lobby.id)
        await _broadcast_lobbies()
        return {"success": True}

    # ------------------------------------------------------------------ #
    #  Jeu                                                                 #
    # ------------------------------------------------------------------ #

    @sio.on("send_guess")
    async def send_guess(sid, data):
        guess = (data or {}).get("guess", "").strip()
        if not guess:
            return {"success": False, "error": ErrorCodes.INVALID_GUESS}

        result = manager.process_guess(sid, guess)

        if not result["success"]:
            return result

        lobby = manager.get_player_lobby(sid)

        # Notifier tous les joueurs du lobby du résultat de ce joueur
        player = lobby.players.get(sid) if lobby else None
        username = player.username if player else sid
        await sio.emit("player_guessed", {
            "sid":      sid,
            "username": username,
            "result":   result["result"],
        }, room=lobby.id if lobby else sid)

        # Si ce joueur a terminé (gagné ou perdu)
        if result["game_over"]:
            await sio.emit("game_over", {
                "has_won": result["has_won"],
                "word":    result["word"],
            }, to=sid)

        # Si tous les joueurs ont terminé → fin de partie globale
        if result["all_done"] and lobby:
            scores = _compute_scores(lobby)
            await sio.emit("game_finished", {
                "word":   lobby.game_state.word,
                "scores": scores,
            }, room=lobby.id)
            await _broadcast_lobbies()

        return result

    @sio.on("replay")
    async def replay(sid, data):
        """Le owner demande une nouvelle partie dans le même lobby."""
        lobby = manager.get_player_lobby(sid)
        if not lobby:
            return {"success": False, "error": ErrorCodes.NOT_IN_LOBBY}
        if lobby.owner_sid != sid:
            return {"success": False, "error": ErrorCodes.NOT_OWNER}

        updated = manager.reset_lobby(lobby.id)
        if updated:
            await sio.emit("lobby_reset", manager.serialize_lobby(lobby.id), room=lobby.id)
            await _broadcast_lobbies()
        return {"success": True}

    # ------------------------------------------------------------------ #
    #  Helpers internes                                                    #
    # ------------------------------------------------------------------ #

    async def _broadcast_lobbies():
        await sio.emit("lobby_list", manager.serialize_lobbies())

    def _compute_scores(lobby) -> list:
        scores = []
        for p in lobby.players.values():
            scores.append({
                "username":     p.username,
                "has_won":      p.has_won,
                "guesses_used": len(p.guesses),
            })
        scores.sort(key=lambda s: (not s["has_won"], s["guesses_used"]))
        return scores
