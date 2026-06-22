import random
import uuid
from typing import Dict, List, Optional

from src.core.models import Lobby, PlayerState, GameState
from src.core.constants import GameConfig, ErrorCodes


class LobbyManager:
    def __init__(self, dictionary: List[str]):
        self.lobbies: Dict[str, Lobby] = {}
        self.player_to_lobby: Dict[str, str] = {}
        self.dictionary = dictionary

    # ------------------------------------------------------------------ #
    #  Gestion des joueurs / lobbies                                       #
    # ------------------------------------------------------------------ #

    def create_lobby(self, owner_sid: str, username: str) -> Lobby:
        if owner_sid in self.player_to_lobby:
            raise ValueError(ErrorCodes.ALREADY_IN_LOBBY)

        lobby_id = self._generate_id()
        player   = PlayerState(sid=owner_sid, username=username)
        lobby    = Lobby(
            id=lobby_id,
            owner_sid=owner_sid,
            players={owner_sid: player},
            max_players=GameConfig.MAX_PLAYERS,
        )
        self.lobbies[lobby_id]          = lobby
        self.player_to_lobby[owner_sid] = lobby_id
        return lobby

    def join_lobby(self, sid: str, username: str, lobby_id: str) -> Lobby:
        lobby_id = lobby_id.upper()

        if sid in self.player_to_lobby:
            raise ValueError(ErrorCodes.ALREADY_IN_LOBBY)
        if lobby_id not in self.lobbies:
            raise ValueError(ErrorCodes.LOBBY_NOT_FOUND)

        lobby = self.lobbies[lobby_id]

        if lobby.is_game_active:
            raise ValueError(ErrorCodes.GAME_ALREADY_STARTED)
        if len(lobby.players) >= lobby.max_players:
            raise ValueError(ErrorCodes.LOBBY_FULL)

        player = PlayerState(sid=sid, username=username)
        lobby.players[sid]       = player
        self.player_to_lobby[sid] = lobby_id
        return lobby

    def leave_lobby(self, sid: str) -> Optional[Lobby]:
        """Retire un joueur de son lobby. Retourne le lobby mis à jour (ou None si supprimé)."""
        lobby_id = self.player_to_lobby.pop(sid, None)
        if not lobby_id or lobby_id not in self.lobbies:
            return None

        lobby = self.lobbies[lobby_id]
        lobby.players.pop(sid, None)

        if not lobby.players:
            del self.lobbies[lobby_id]
            return None

        # Transfert de ownership si nécessaire
        if lobby.owner_sid == sid:
            lobby.owner_sid = next(iter(lobby.players))

        return lobby

    def set_ready(self, sid: str, ready: bool) -> Optional[Lobby]:
        lobby = self.get_player_lobby(sid)
        if not lobby:
            return None
        player = lobby.players.get(sid)
        if player:
            player.is_ready = ready
        return lobby

    def get_player_lobby(self, sid: str) -> Optional[Lobby]:
        lobby_id = self.player_to_lobby.get(sid)
        return self.lobbies.get(lobby_id) if lobby_id else None

    # ------------------------------------------------------------------ #
    #  Logique de jeu                                                      #
    # ------------------------------------------------------------------ #

    def start_game(self, sid: str) -> Lobby:
        lobby = self.get_player_lobby(sid)
        if not lobby:
            raise ValueError(ErrorCodes.NOT_IN_LOBBY)
        if lobby.owner_sid != sid:
            raise ValueError(ErrorCodes.NOT_OWNER)
        if lobby.is_game_active:
            raise ValueError(ErrorCodes.GAME_ALREADY_STARTED)
        if not lobby.all_players_ready:
            raise ValueError(ErrorCodes.NOT_ALL_READY)

        word = random.choice(self.dictionary)
        lobby.game_state = GameState(word=word, is_active=True, is_finished=False)

        # Reset des états joueurs
        for player in lobby.players.values():
            player.guesses  = []
            player.has_won  = False
            player.has_lost = False
            player.is_ready = False

        print(f"[GAME] Lobby {lobby.id} — mot : {word}")
        return lobby

    def process_guess(self, sid: str, guess: str) -> dict:
        """
        Traite un guess d'un joueur.
        Retourne un dict avec le résultat ou une erreur.
        """
        from src.core.logic import compare_guess, validate_guess

        lobby = self.get_player_lobby(sid)
        if not lobby:
            return {"success": False, "error": ErrorCodes.NOT_IN_LOBBY}
        if not lobby.is_game_active:
            return {"success": False, "error": ErrorCodes.GAME_NOT_STARTED}

        player = lobby.players.get(sid)
        if not player:
            return {"success": False, "error": ErrorCodes.NOT_IN_LOBBY}
        if player.is_done:
            return {"success": False, "error": ErrorCodes.GAME_OVER}

        target = lobby.game_state.word
        is_valid, error_code = validate_guess(guess, target, self.dictionary)
        if not is_valid:
            return {"success": False, "error": error_code}

        result = compare_guess(guess, target)
        player.guesses.append(result)

        if result.is_correct:
            player.has_won = True
        elif len(player.guesses) >= GameConfig.MAX_TRIES:
            player.has_lost = True

        # Vérifier si tous les joueurs ont terminé
        all_done = all(p.is_done for p in lobby.players.values())
        if all_done:
            lobby.game_state.is_active  = False
            lobby.game_state.is_finished = True

        return {
            "success":   True,
            "result":    result.to_dict(),
            "game_over": player.is_done,
            "has_won":   player.has_won,
            "all_done":  all_done,
            "word":      target if player.is_done else None,
        }

    def reset_lobby(self, lobby_id: str) -> Optional[Lobby]:
        """Remet le lobby en état d'attente pour une nouvelle partie."""
        lobby = self.lobbies.get(lobby_id)
        if not lobby:
            return None
        lobby.game_state = None
        for player in lobby.players.values():
            player.guesses  = []
            player.has_won  = False
            player.has_lost = False
            player.is_ready = False
        return lobby

    # ------------------------------------------------------------------ #
    #  Sérialisation                                                       #
    # ------------------------------------------------------------------ #

    def serialize_lobbies(self) -> List[dict]:
        return [l.to_list_dict() for l in self.lobbies.values()]

    def serialize_lobby(self, lobby_id: str) -> Optional[dict]:
        lobby = self.lobbies.get(lobby_id)
        return lobby.to_room_dict() if lobby else None

    # ------------------------------------------------------------------ #
    #  Utilitaires                                                         #
    # ------------------------------------------------------------------ #

    def _generate_id(self) -> str:
        while True:
            lid = str(uuid.uuid4())[:GameConfig.LOBBY_ID_LENGTH].upper()
            if lid not in self.lobbies:
                return lid
