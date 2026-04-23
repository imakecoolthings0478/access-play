"""Game selection hub."""

import pygame

from games.maze_runner import MazeRunner
from games.memory_match import MemoryMatch
from games.reaction_blaster import ReactionBlaster
from games.word_builder import WordBuilder
from settings import CYAN, FONT_SIZES, GREEN, PURPLE, RED, SCREEN_WIDTH, WHITE, YELLOW
from utils.save_manager import load_scores
from utils.ui_components import draw_background, draw_button, draw_card, draw_text, load_font


class GameHubScreen:
    """Shows four accessible games in a 2x2 grid."""

    def __init__(self, app):
        """Create card rectangles and game metadata."""
        self.app = app
        self.cards = [
            pygame.Rect(110, 170, 445, 170),
            pygame.Rect(645, 170, 445, 170),
            pygame.Rect(110, 390, 445, 170),
            pygame.Rect(645, 390, 445, 170),
        ]
        self.back_rect = pygame.Rect(90, 635, 150, 66)
        self.settings_rect = pygame.Rect(930, 635, 180, 66)
        self.stats_rect = pygame.Rect(735, 635, 170, 66)
        self.games = [
            ("Maze Runner", "Navigate a glowing ball through a maze", MazeRunner, GREEN),
            ("Memory Match", "Match all card pairs with scanning", MemoryMatch, PURPLE),
            ("Reaction Blaster", "Hit targets before they expire", ReactionBlaster, RED),
            ("Word Builder", "Choose letters to solve word hints", WordBuilder, YELLOW),
        ]

    def on_enter(self):
        """Reload scores when returning to the hub."""
        self.scores = load_scores()

    def handle_events(self, events):
        """Start games or navigate with selected cards."""
        rects = self.cards + [self.back_rect, self.stats_rect, self.settings_rect]
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command in {"select", "yes"}:
            selected = self.app.switch_mode.get_selected_index()
        if selected is None:
            return
        if selected < 4:
            self.app.current_screen = self.games[selected][2](self.app)
            self.app.current_screen.on_enter()
        elif selected == 4:
            self.app.set_screen("home")
        elif selected == 5:
            self.app.set_screen("stats")
        elif selected == 6:
            self.app.set_screen("settings")

    def update(self, elapsed):
        """Update hub animations."""
        return

    def draw(self, surface):
        """Draw the game cards and navigation."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Game Hub", (90, 74), load_font(FONT_SIZES["heading"], True), CYAN)
        for index, rect in enumerate(self.cards):
            title, description, _cls, color = self.games[index]
            draw_card(surface, rect, title, description, color)
            self._draw_icon(surface, rect, index, color)
            high = self._high_score_text(index)
            draw_text(surface, high, (rect.x + 96, rect.y + 112), load_font(18), WHITE)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Back", PURPLE, self.back_rect.collidepoint(mouse))
        draw_button(surface, self.stats_rect, "Stats", CYAN, self.stats_rect.collidepoint(mouse))
        draw_button(surface, self.settings_rect, "Settings", GREEN, self.settings_rect.collidepoint(mouse))

    def _draw_icon(self, surface, rect, index, color):
        """Draw a small game-specific icon."""
        center = (rect.x + 54, rect.y + 58)
        if index == 0:
            pygame.draw.rect(surface, color, (center[0] - 22, center[1] - 22, 44, 44), 4)
            pygame.draw.circle(surface, color, center, 8)
        elif index == 1:
            for x in range(2):
                for y in range(2):
                    pygame.draw.rect(surface, color, (center[0] - 24 + x * 26, center[1] - 24 + y * 26, 20, 20), border_radius=5)
        elif index == 2:
            pygame.draw.circle(surface, color, center, 24, 4)
            pygame.draw.circle(surface, color, center, 9)
        else:
            draw_text(surface, "A", center, load_font(34, True), color, center=True)

    def _high_score_text(self, index):
        """Return a score summary for the card."""
        if index == 0:
            best = self.scores.get("maze_runner", {}).get("best_time")
            return f"Best time: {best}s" if best else "No run yet"
        if index == 1:
            moves = self.scores.get("memory_match", {}).get("best_moves")
            return f"Best moves: {moves}" if moves else "No match yet"
        if index == 2:
            score = self.scores.get("reaction_blaster", {}).get("best_score", 0)
            return f"Best score: {score}"
        score = self.scores.get("word_builder", {}).get("best_score", 0)
        return f"Best score: {score}"
