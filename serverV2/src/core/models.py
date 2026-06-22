from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Color(Enum):
    GREEN  = "green"
    YELLOW = "yellow"
    GRAY   = "gray"


@dataclass
class GuessChar:
    char: str
    color: Color

    def to_dict(self) -> dict:
        return {"char": self.char, "color": self.color.value}


@dataclass
class GuessResult:
    word: str
    feedback: List[GuessChar]
    is_correct: bool

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "feedback": [g.to_dict() for g in self.feedback],
            "is_correct": self.is_correct,
        }


@dataclass
class PlayerState:
    sid: str
    username: str
    is_ready: bool = False
    guesses: List[GuessResult] = field(default_factory=list)
    has_won: bool = False
    has_lost: bool = False

    @property
    def tries_left(self) -> int:
        from src.core.constants import GameConfig
        return GameConfig.MAX_TRIES - len(self.guesses)

    @property
    def is_done(self) -> bool:
        return self.has_won or self.has_lost

    def to_dict(self) -> dict:
        return {
            "sid": self.sid,
            "username": self.username,
            "is_ready": self.is_ready,
            "guesses_count": len(self.guesses),
            "has_won": self.has_won,
            "has_lost": self.has_lost,
        }


@dataclass
class GameState:
    word: str
    is_active: bool = True
    is_finished: bool = False

    def to_dict(self) -> dict:
        return {
            "is_active": self.is_active,
            "is_finished": self.is_finished,
            "word_length": len(self.word),
            "first_char": self.word[0] if self.word else "",
        }


@dataclass
class Lobby:
    id: str
    owner_sid: str
    players: Dict[str, PlayerState] = field(default_factory=dict)
    game_state: Optional[GameState] = None
    max_players: int = 8

    @property
    def is_game_active(self) -> bool:
        return self.game_state is not None and self.game_state.is_active

    @property
    def all_players_ready(self) -> bool:
        non_owner = [p for sid, p in self.players.items() if sid != self.owner_sid]
        if not non_owner:
            return True  # owner seul = peut démarrer
        return all(p.is_ready for p in non_owner)

    def to_list_dict(self) -> dict:
        """Sérialisation légère pour la liste des lobbies."""
        return {
            "id": self.id,
            "owner_sid": self.owner_sid,
            "players_count": len(self.players),
            "max_players": self.max_players,
            "is_active": self.is_game_active,
        }

    def to_room_dict(self) -> dict:
        """Sérialisation complète pour la vue salle d'attente."""
        return {
            "id": self.id,
            "owner_sid": self.owner_sid,
            "players": {sid: p.to_dict() for sid, p in self.players.items()},
            "game_active": self.is_game_active,
            "word_length": len(self.game_state.word) if self.game_state else 0,
        }
