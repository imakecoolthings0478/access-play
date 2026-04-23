"""Stats and achievements screen."""

import math

import pygame

from settings import CYAN, FONT_SIZES, GREEN, MUTED, PURPLE, RED, SCREEN_WIDTH, WHITE, YELLOW
from utils.save_manager import load_scores
from utils.ui_components import draw_background, draw_button, draw_frosted_card, draw_text, load_font


ACHIEVEMENTS = [
    "First Win",
    "10 Games Played",
    "Speed Demon",
    "Perfect Memory",
    "Sharp Shooter",
]


class StatsScreen:
    """Displays saved scores and unlocked achievement badges."""

    def __init__(self, app):
        """Create the screen and navigation button."""
        self.app = app
        self.back_rect = pygame.Rect(80, 635, 150, 66)
        self.scores = load_scores()

    def on_enter(self):
        """Reload scores every time the screen opens."""
        self.scores = load_scores()

    def handle_events(self, events):
        """Return to the home screen when Back is selected."""
        selected, command = self.app.get_action(events, [self.back_rect])
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.back_rect.collidepoint(mouse):
                selected = 0
        if selected == 0 or command in {"select", "no"}:
            self.app.set_screen("home")

    def update(self, elapsed):
        """Stats are static, so no update is required."""
        return

    def draw(self, surface):
        """Draw score cards and achievement hexagons."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Stats", (80, 72), load_font(FONT_SIZES["heading"], True), CYAN)
        draw_frosted_card(surface, pygame.Rect(80, 145, 500, 400), PURPLE)
        draw_frosted_card(surface, pygame.Rect(630, 145, 490, 400), CYAN)
        lines = [
            f"Games played: {self.scores.get('games_played', 0)}",
            f"Total play time: {self.scores.get('total_time', 0)} seconds",
            f"Maze best: {self.scores.get('maze_runner', {}).get('best_time', 'None')}s",
            f"Memory best moves: {self.scores.get('memory_match', {}).get('best_moves', 'None')}",
            f"Blaster best score: {self.scores.get('reaction_blaster', {}).get('best_score', 0)}",
            f"Word best score: {self.scores.get('word_builder', {}).get('best_score', 0)}",
        ]
        for index, line in enumerate(lines):
            draw_text(surface, line, (125, 190 + index * 52), load_font(24), WHITE)
        draw_text(surface, "Achievements", (665, 190), load_font(28, True), WHITE)
        unlocked = self.scores.get("achievements", [])
        for index, name in enumerate(ACHIEVEMENTS):
            x = 705 + (index % 2) * 205
            y = 285 + (index // 2) * 110
            self._draw_hex(surface, (x, y), name, name in unlocked)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Back", RED, self.back_rect.collidepoint(mouse))

    def _draw_hex(self, surface, center, name, unlocked):
        """Draw a glowing achievement badge."""
        color = GREEN if unlocked else MUTED
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            points.append((center[0] + math.cos(angle) * 44, center[1] + math.sin(angle) * 44))
        pygame.draw.polygon(surface, color, points, width=4)
        label = name if unlocked else "Locked"
        draw_text(surface, label, (center[0], center[1] + 60), load_font(17), color, center=True)
