from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PlayerInfo:
    username: str
    is_ready: bool
    guesses_count: int
    has_won: bool = False
    has_lost: bool = False


@dataclass
class LobbyInfo:
    id: str
    owner_sid: str
    players: Dict[str, PlayerInfo] = field(default_factory=dict)
    game_active: bool = False
    word_length: int = 0

    @staticmethod
    def from_dict(data: dict) -> 'LobbyInfo':
        players = {
            sid: PlayerInfo(
                username=p["username"],
                is_ready=p["is_ready"],
                guesses_count=p["guesses_count"],
                has_won=p.get("has_won", False),
                has_lost=p.get("has_lost", False),
            )
            for sid, p in data.get("players", {}).items()
        }
        return LobbyInfo(
            id=data["id"],
            owner_sid=data["owner_sid"],
            players=players,
            game_active=data.get("game_active", False),
            word_length=data.get("word_length", 0),
        )
