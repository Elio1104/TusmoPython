from typing import List
from src.core.models import GuessResult, GuessChar, Color
from src.core.constants import GameConfig


def compare_guess(guess: str, target: str) -> GuessResult:
    """
    Compare un guess avec le mot cible (Tusmo).
    Retourne un GuessResult avec le feedback lettre par lettre.
    """
    guess  = guess.upper()
    target = target.upper()

    feedback    = [Color.GRAY] * len(guess)
    target_pool = list(target)

    # 1er passage : lettres exactes (GREEN)
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            feedback[i]    = Color.GREEN
            target_pool[i] = None

    # 2ème passage : lettres présentes mais mal placées (YELLOW)
    for i, g in enumerate(guess):
        if feedback[i] == Color.GREEN:
            continue
        if g in target_pool:
            feedback[i] = Color.YELLOW
            target_pool[target_pool.index(g)] = None

    chars      = [GuessChar(char=c, color=col) for c, col in zip(guess, feedback)]
    is_correct = all(col == Color.GREEN for col in feedback)

    return GuessResult(word=guess, feedback=chars, is_correct=is_correct)


def validate_guess(guess: str, target: str, dictionary: List[str]) -> tuple[bool, str]:
    """
    Valide un guess avant de le traiter.
    Retourne (is_valid, error_code).
    """
    from src.core.constants import ErrorCodes

    guess = guess.strip().upper()

    if len(guess) != len(target):
        return False, ErrorCodes.WRONG_LENGTH

    if guess not in [w.upper() for w in dictionary]:
        return False, ErrorCodes.WORD_NOT_IN_DICT

    return True, ""


def load_dictionary(filepath: str) -> List[str]:
    """Charge un fichier dictionnaire et retourne une liste de mots en majuscules."""
    from pathlib import Path
    p = Path(filepath)
    if not p.exists():
        print(f"[WARN] Dictionnaire introuvable : {filepath}")
        return []
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        words = [
            line.strip().upper()
            for line in f
            if line.strip()
            and GameConfig.MIN_WORD_LENGTH <= len(line.strip()) <= GameConfig.MAX_WORD_LENGTH
        ]
    print(f"[INFO] Dictionnaire chargé : {len(words)} mots depuis {p.name}")
    return words
