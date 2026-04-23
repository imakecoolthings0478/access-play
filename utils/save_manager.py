"""JSON save helpers for the small local data files.

The project uses plain JSON instead of a database because the saved data is
simple and easy to inspect during marking.
"""

import json
from copy import deepcopy

from settings import DATA_DIR, PROFILE_PATH, SCORES_PATH


DEFAULT_PROFILE = {
    "name": "",
    "avatar": 0,
    "disability": "Limited hand mobility",
    "sensitivity": 5,
    "input_mode": "Single Key Mode",
    "dwell_time": 1.5,
    "scan_speed": 1.5,
    "font_size": "Normal",
    "high_contrast": False,
    "sound": True,
    "cursor_size": "Medium",
    "paused_game": None,
}

DEFAULT_SCORES = {
    "games_played": 0,
    "total_time": 0,
    "maze_runner": {},
    "memory_match": {"best_moves": None, "best_time": None, "perfect": False},
    "reaction_blaster": {"best_score": 0, "best_streak": 0},
    "word_builder": {"best_score": 0},
    "achievements": [],
}


def _read_json(path, fallback):
    """Read a JSON dictionary and merge it over a default template."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            merged = deepcopy(fallback)
            if isinstance(data, dict):
                merged.update(data)
            return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return deepcopy(fallback)


def _write_json(path, data):
    """Write data in a readable format so the save files are easy to check."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_profile():
    """Load the saved profile and settings."""
    return _read_json(PROFILE_PATH, DEFAULT_PROFILE)


def save_profile(data):
    """Save all profile fields to disk."""
    profile = load_profile()
    profile.update(data)
    _write_json(PROFILE_PATH, profile)


def load_settings():
    """Return settings, which are stored together with the profile."""
    return load_profile()


def save_settings(data):
    """Save settings while keeping existing profile details."""
    save_profile(data)


def load_scores():
    """Load local score and achievement data."""
    return _read_json(SCORES_PATH, DEFAULT_SCORES)


def save_scores(data):
    """Save a score dictionary without throwing away existing sections."""
    scores = load_scores()
    scores.update(data)
    _write_json(SCORES_PATH, scores)


def add_achievement(name):
    """Add an achievement badge if it is not already unlocked."""
    scores = load_scores()
    achievements = scores.setdefault("achievements", [])
    if name not in achievements:
        achievements.append(name)
    save_scores(scores)


def record_game_play(seconds):
    """Increase global game counters after a game finishes."""
    scores = load_scores()
    scores["games_played"] = scores.get("games_played", 0) + 1
    scores["total_time"] = scores.get("total_time", 0) + int(seconds)
    if scores["games_played"] >= 10:
        add_achievement("10 Games Played")
    save_scores(scores)


def save_score(game_name, score=None, time_taken=None, extra=None):
    """Save a best score or best time for a named game."""
    scores = load_scores()
    game = scores.setdefault(game_name, {})
    if score is not None:
        current = game.get("best_score", 0)
        game["best_score"] = max(current, score)
    if time_taken is not None:
        current_time = game.get("best_time")
        if current_time is None or time_taken < current_time:
            game["best_time"] = round(time_taken, 2)
    if extra:
        if "best_moves" in extra:
            current_moves = game.get("best_moves")
            moves = extra["best_moves"]
            game["best_moves"] = moves if current_moves is None else min(current_moves, moves)
        if "best_streak" in extra:
            game["best_streak"] = max(game.get("best_streak", 0), extra["best_streak"])
        if "perfect" in extra:
            game["perfect"] = bool(game.get("perfect", False) or extra["perfect"])
        for key, value in extra.items():
            if key not in {"best_moves", "best_streak", "perfect"}:
                game[key] = value
    save_scores(scores)


def save_paused_game(game_name, state):
    """Store paused game progress so it can be resumed later."""
    profile = load_profile()
    profile["paused_game"] = {"game": game_name, "state": state}
    _write_json(PROFILE_PATH, profile)


def clear_paused_game():
    """Remove any saved paused-game state."""
    profile = load_profile()
    profile["paused_game"] = None
    _write_json(PROFILE_PATH, profile)
