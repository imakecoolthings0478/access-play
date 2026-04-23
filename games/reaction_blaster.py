"""Reaction Blaster game."""

import random
import time

import pygame

from settings import CYAN, FONT_SIZES, GREEN, PURPLE, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW
from utils.save_manager import add_achievement, clear_paused_game, record_game_play, save_paused_game, save_score
from utils.ui_components import draw_background, draw_button, draw_text, load_font


class ReactionBlaster:
    """A target-clicking reaction game with shrinking timers."""

    def __init__(self, app):
        """Create game state."""
        self.app = app
        self.back_rect = pygame.Rect(70, 660, 140, 62)
        self.targets = []
        self.score = 0
        self.misses = 0
        self.streak = 0
        self.best_streak = 0
        self.spawn_timer = 0
        self.started = time.time()
        self.paused = False
        self.game_over = False

    def on_enter(self):
        """Prepare the game when launched."""
        return

    def handle_events(self, events):
        """Handle target selection and pause."""
        target_rects = [pygame.Rect(t["x"] - t["r"], t["y"] - t["r"], t["r"] * 2, t["r"] * 2) for t in self.targets]
        rects = target_rects + [self.back_rect]
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self._toggle_pause()
                if event.key == pygame.K_SPACE:
                    selected = self._target_at(mouse)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command == "pause":
            self._toggle_pause()
        if command == "fire":
            selected = self._target_at(self.app.head_tracker.get_cursor_position())
        if selected == len(self.targets):
            self.app.set_screen("hub")
        elif selected is not None and 0 <= selected < len(self.targets) and not self.paused and not self.game_over:
            self._hit(selected)

    def _target_at(self, pos):
        """Return the index of the target containing a position."""
        for index, target in enumerate(self.targets):
            if (pos[0] - target["x"]) ** 2 + (pos[1] - target["y"]) ** 2 <= target["r"] ** 2:
                return index
        return None

    def _hit(self, index):
        """Remove a hit target and award points."""
        self.targets.pop(index)
        self.streak += 1
        self.best_streak = max(self.best_streak, self.streak)
        self.score += 20 if self.streak >= 3 else 10
        if self.best_streak >= 10:
            add_achievement("Sharp Shooter")

    def _spawn(self):
        """Add a target at a random screen position."""
        lifetime = max(1.0, 2.6 - self.score / 120)
        self.targets.append({
            "x": random.randint(130, SCREEN_WIDTH - 130),
            "y": random.randint(150, SCREEN_HEIGHT - 170),
            "r": random.randint(28, 46),
            "life": lifetime,
            "max_life": lifetime,
            "color": random.choice([CYAN, PURPLE, GREEN, YELLOW]),
        })

    def _toggle_pause(self):
        """Pause or resume and save partial progress."""
        self.paused = not self.paused
        if self.paused:
            save_paused_game("reaction_blaster", {"score": self.score, "misses": self.misses})

    def update(self, elapsed):
        """Spawn targets and expire old ones."""
        if self.paused or self.game_over:
            return
        self.spawn_timer -= elapsed
        if self.spawn_timer <= 0:
            self._spawn()
            self.spawn_timer = max(0.45, 1.3 - self.score / 180)
        for target in list(self.targets):
            target["life"] -= elapsed
            if target["life"] <= 0:
                self.targets.remove(target)
                self.misses += 1
                self.streak = 0
                if self.misses >= 3:
                    self._finish()

    def _finish(self):
        """End the game and save the score."""
        self.game_over = True
        elapsed = time.time() - self.started
        save_score("reaction_blaster", score=self.score, extra={"best_streak": self.best_streak})
        record_game_play(elapsed)
        clear_paused_game()

    def draw(self, surface):
        """Draw targets, score, and game-over state."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Reaction Blaster", (70, 50), load_font(FONT_SIZES["heading"], True), CYAN)
        draw_text(surface, f"Score: {self.score}   Misses: {self.misses}/3   Streak: {self.streak}", (620, 65), load_font(24), WHITE)
        for target in self.targets:
            ratio = target["life"] / target["max_life"]
            pygame.draw.circle(surface, target["color"], (target["x"], target["y"]), target["r"])
            pygame.draw.circle(surface, WHITE, (target["x"], target["y"]), int(target["r"] + 12 * ratio), 4)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Hub", RED, self.back_rect.collidepoint(mouse))
        if self.game_over:
            draw_text(surface, "Game Over", (SCREEN_WIDTH // 2, 650), load_font(34, True), RED, center=True)
        if self.paused:
            draw_text(surface, "Paused", (SCREEN_WIDTH // 2, 650), load_font(34, True), WHITE, center=True)
