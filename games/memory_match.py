"""Memory Match game."""

import random
import time

import pygame

from settings import CYAN, FONT_SIZES, GREEN, PURPLE, RED, SCREEN_WIDTH, WHITE
from utils.save_manager import add_achievement, clear_paused_game, record_game_play, save_paused_game, save_score
from utils.ui_components import draw_background, draw_button, draw_text, load_font


class MemoryMatch:
    """A 4x4 card matching game."""

    def __init__(self, app):
        """Create cards and counters."""
        self.app = app
        self.back_rect = pygame.Rect(70, 660, 140, 62)
        self.cards = []
        self.new_game()

    def on_enter(self):
        """Prepare the game when opened."""
        return

    def new_game(self):
        """Shuffle eight matching pairs into sixteen cards."""
        values = list(range(8)) * 2
        random.shuffle(values)
        self.cards = [{"value": value, "face": False, "done": False} for value in values]
        self.rects = [pygame.Rect(260 + (i % 4) * 165, 140 + (i // 4) * 120, 125, 90) for i in range(16)]
        self.open_cards = []
        self.moves = 0
        self.wrong = 0
        self.flip_back_at = 0
        self.started = time.time()
        self.paused = False
        self.won = False

    def handle_events(self, events):
        """Flip cards using mouse, dwell, scanning, voice, or number keys."""
        rects = self.rects + [self.back_rect]
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        card_words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen"]
        if command and command.startswith("card "):
            word = command.replace("card ", "")
            if word in card_words:
                selected = card_words.index(word)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self._toggle_pause()
                if pygame.K_1 <= event.key <= pygame.K_9:
                    selected = event.key - pygame.K_1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command == "pause":
            self._toggle_pause()
        if selected == 16:
            self.app.set_screen("hub")
        elif selected is not None and 0 <= selected < 16 and not self.paused:
            self._flip(selected)

    def _flip(self, index):
        """Flip a card and check for a match."""
        card = self.cards[index]
        if card["face"] or card["done"] or len(self.open_cards) == 2:
            return
        card["face"] = True
        self.open_cards.append(index)
        if len(self.open_cards) == 2:
            self.moves += 1
            a, b = self.open_cards
            if self.cards[a]["value"] == self.cards[b]["value"]:
                self.cards[a]["done"] = self.cards[b]["done"] = True
                self.open_cards = []
                if all(card["done"] for card in self.cards):
                    self._win()
            else:
                self.wrong += 1
                self.flip_back_at = pygame.time.get_ticks() + 700

    def _toggle_pause(self):
        """Pause or resume the game and save progress."""
        self.paused = not self.paused
        if self.paused:
            save_paused_game("memory_match", {"moves": self.moves})

    def _win(self):
        """Save best memory result."""
        self.won = True
        elapsed = time.time() - self.started
        save_score("memory_match", time_taken=elapsed, extra={"best_moves": self.moves, "perfect": self.wrong == 0})
        record_game_play(elapsed)
        add_achievement("First Win")
        if self.wrong == 0:
            add_achievement("Perfect Memory")
        clear_paused_game()

    def update(self, elapsed):
        """Turn unmatched cards back over after a short delay."""
        if self.flip_back_at and pygame.time.get_ticks() >= self.flip_back_at:
            for index in self.open_cards:
                self.cards[index]["face"] = False
            self.open_cards = []
            self.flip_back_at = 0

    def draw(self, surface):
        """Draw cards, moves, and win state."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Memory Match", (70, 50), load_font(FONT_SIZES["heading"], True), CYAN)
        draw_text(surface, f"Moves: {self.moves}", (900, 65), load_font(26), WHITE)
        colors = [(0, 240, 255), (123, 47, 255), (86, 230, 153), (255, 91, 111), (255, 211, 95), (91, 141, 255), (255, 120, 210), (120, 255, 210)]
        for index, rect in enumerate(self.rects):
            card = self.cards[index]
            color = colors[card["value"]] if card["face"] or card["done"] else (28, 36, 60)
            pygame.draw.rect(surface, color, rect, border_radius=14)
            pygame.draw.rect(surface, PURPLE, rect, 3, border_radius=14)
            text = str(card["value"] + 1) if card["face"] or card["done"] else "?"
            draw_text(surface, text, rect.center, load_font(34, True), WHITE, center=True)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Hub", RED, self.back_rect.collidepoint(mouse))
        if self.won:
            draw_text(surface, "All pairs matched!", (SCREEN_WIDTH // 2, 650), load_font(31, True), GREEN, center=True)
        if self.paused:
            draw_text(surface, "Paused", (SCREEN_WIDTH // 2, 650), load_font(31, True), WHITE, center=True)
