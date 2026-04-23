"""Word Builder game."""

import random
import time

import pygame

from settings import CYAN, FONT_SIZES, GREEN, MUTED, PURPLE, RED, SCREEN_WIDTH, WHITE
from utils.save_manager import add_achievement, clear_paused_game, record_game_play, save_paused_game, save_score
from utils.ui_components import draw_background, draw_button, draw_text, load_font


WORDS = {
    "Animals": [
        ("TIGER", "Striped big cat"), ("HORSE", "Animal people ride"), ("WHALE", "Largest ocean mammal"),
        ("EAGLE", "Sharp-eyed bird"), ("ZEBRA", "Black and white stripes"), ("PANDA", "Bamboo eater"),
        ("SNAKE", "Legless reptile"), ("KOALA", "Australian tree animal"), ("OTTER", "Playful water mammal"),
        ("CAMEL", "Desert animal with humps"),
    ],
    "Countries": [
        ("INDIA", "Country with New Delhi"), ("JAPAN", "Island nation in East Asia"), ("BRAZIL", "Home of Amazon rainforest"),
        ("EGYPT", "Country of ancient pyramids"), ("FRANCE", "Country with Paris"), ("CANADA", "Large North American country"),
        ("NEPAL", "Country of Mount Everest"), ("SPAIN", "Country with Madrid"), ("KENYA", "East African country"),
        ("ITALY", "Boot-shaped country"),
    ],
    "Sports": [
        ("CRICKET", "Bat and ball sport"), ("TENNIS", "Racket sport with a net"), ("HOCKEY", "Stick and goal sport"),
        ("BOXING", "Ring combat sport"), ("SKATING", "Sport on ice or wheels"), ("CYCLING", "Racing on bicycles"),
        ("SWIMMING", "Sport in water"), ("KABADDI", "Indian contact team sport"), ("FOOTBALL", "Goal-scoring team sport"),
        ("CHESS", "Board sport with kings"),
    ],
}


class WordBuilder:
    """A letter-selection word guessing game."""

    def __init__(self, app):
        """Create word puzzle state."""
        self.app = app
        self.back_rect = pygame.Rect(70, 660, 140, 62)
        self.category_rects = [pygame.Rect(90 + i * 220, 115, 190, 62) for i in range(3)]
        self.letter_rects = [pygame.Rect(130 + (i % 7) * 135, 355 + (i // 7) * 70, 86, 54) for i in range(26)]
        self.category = "Animals"
        self.started = time.time()
        self.score = 100
        self.paused = False
        self.won = False
        self._choose_word()

    def on_enter(self):
        """Prepare the game when opened."""
        return

    def _choose_word(self):
        """Select a new random word for the active category."""
        self.answer, self.hint = random.choice(WORDS[self.category])
        self.guessed = set()
        self.wrong = set()
        self.won = False

    def handle_events(self, events):
        """Handle letter, category, pause, and back selections."""
        rects = self.category_rects + self.letter_rects + [self.back_rect]
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self._toggle_pause()
                if pygame.K_a <= event.key <= pygame.K_z:
                    self._select_letter(chr(event.key).upper())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command == "pause":
            self._toggle_pause()
        if selected is None:
            return
        if selected < 3:
            self.category = list(WORDS.keys())[selected]
            self._choose_word()
        elif selected < 29 and not self.paused:
            self._select_letter(chr(ord("A") + selected - 3))
        elif selected == 29:
            self.app.set_screen("hub")

    def _select_letter(self, letter):
        """Apply a guessed letter and save the game if solved."""
        if self.paused or self.won or letter in self.guessed or letter in self.wrong:
            return
        if letter in self.answer:
            self.guessed.add(letter)
            if all(ch in self.guessed for ch in self.answer):
                self._win()
        else:
            self.wrong.add(letter)
            self.score = max(0, self.score - 8)

    def _win(self):
        """Save the completed word score."""
        self.won = True
        elapsed = time.time() - self.started
        save_score("word_builder", score=self.score)
        record_game_play(elapsed)
        add_achievement("First Win")
        clear_paused_game()

    def _toggle_pause(self):
        """Pause or resume and store current puzzle information."""
        self.paused = not self.paused
        if self.paused:
            save_paused_game("word_builder", {"category": self.category, "answer": self.answer, "score": self.score})

    def update(self, elapsed):
        """Word Builder updates through input only."""
        return

    def draw(self, surface):
        """Draw hint, answer blanks, letter grid, and categories."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Word Builder", (70, 45), load_font(FONT_SIZES["heading"], True), CYAN)
        mouse = pygame.mouse.get_pos()
        for index, rect in enumerate(self.category_rects):
            label = list(WORDS.keys())[index]
            draw_button(surface, rect, label, GREEN if label == self.category else PURPLE, rect.collidepoint(mouse))
        draw_text(surface, f"Hint: {self.hint}", (SCREEN_WIDTH // 2, 225), load_font(29, True), WHITE, center=True)
        start_x = SCREEN_WIDTH // 2 - len(self.answer) * 35
        for index, letter in enumerate(self.answer):
            rect = pygame.Rect(start_x + index * 70, 280, 52, 54)
            pygame.draw.rect(surface, (28, 36, 60), rect, border_radius=8)
            pygame.draw.rect(surface, CYAN, rect, 3, border_radius=8)
            visible = letter if letter in self.guessed else ""
            draw_text(surface, visible, rect.center, load_font(28, True), GREEN, center=True)
        for index, rect in enumerate(self.letter_rects):
            letter = chr(ord("A") + index)
            if letter in self.guessed:
                color = GREEN
            elif letter in self.wrong:
                color = RED
            else:
                color = PURPLE
            draw_button(surface, rect, letter, color, rect.collidepoint(mouse))
        draw_text(surface, f"Score: {self.score}", (905, 125), load_font(26), WHITE)
        draw_button(surface, self.back_rect, "Hub", RED, self.back_rect.collidepoint(mouse))
        if self.won:
            draw_text(surface, "Correct word!", (SCREEN_WIDTH // 2, 650), load_font(32, True), GREEN, center=True)
        if self.paused:
            draw_text(surface, "Paused", (SCREEN_WIDTH // 2, 650), load_font(32, True), MUTED, center=True)
