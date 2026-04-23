"""Global constants used by the AccessPlay application."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FONT_DIR = BASE_DIR / "assets" / "fonts"
PROFILE_PATH = DATA_DIR / "profile.json"
SCORES_PATH = DATA_DIR / "scores.json"

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 760
FPS = 60

BACKGROUND = (7, 11, 20)
PANEL = (18, 24, 42)
PANEL_LIGHT = (33, 42, 70)
WHITE = (245, 250, 255)
MUTED = (160, 176, 196)
CYAN = (0, 240, 255)
PURPLE = (123, 47, 255)
GREEN = (86, 230, 153)
RED = (255, 91, 111)
YELLOW = (255, 211, 95)
BLACK = (0, 0, 0)

HIGH_CONTRAST = {
    "background": (0, 0, 0),
    "panel": (16, 16, 16),
    "text": (255, 255, 255),
    "accent": (255, 255, 255),
}

FONT_NAME = "arial"
FONT_SIZES = {
    "small": 18,
    "body": 24,
    "heading": 42,
    "title": 76,
}

BUTTON_MIN_SIZE = 60
DEFAULT_DWELL_TIME = 1.5
DEFAULT_SCAN_SPEED = 1.5
DEFAULT_SENSITIVITY = 5
CURSOR_SIZES = {"Small": 12, "Medium": 20, "Large": 30}
INPUT_MODES = ["Head Tracking", "Voice Control", "Single Key Mode"]

VOICE_COMMANDS = {
    "up", "down", "left", "right", "jump", "fire", "pause", "select",
    "yes", "no", "card one", "card two", "card three", "card four",
    "card five", "card six", "card seven", "card eight", "card nine",
    "card ten", "card eleven", "card twelve", "card thirteen",
    "card fourteen", "card fifteen", "card sixteen",
}

MAZE_CELL = 34
AVATARS = [
    ("AP", CYAN),
    ("G", PURPLE),
    ("S", GREEN),
    ("R", RED),
    ("Y", YELLOW),
    ("B", (91, 141, 255)),
]
DISABILITY_OPTIONS = [
    "Limited hand mobility",
    "No hand use",
    "Low vision",
    "Other",
]
