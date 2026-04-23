"""Home screen with hero title and input choices."""

import pygame

from settings import CYAN, FONT_SIZES, INPUT_MODES, MUTED, PURPLE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from utils.ui_components import draw_background, draw_button, draw_card, draw_text, load_font


class HomeScreen:
    """Shows the main landing screen for AccessPlay."""

    def __init__(self, app):
        """Store the app reference and build button rectangles."""
        self.app = app
        self.cards = [
            pygame.Rect(90, 300, 315, 150),
            pygame.Rect(442, 300, 315, 150),
            pygame.Rect(794, 300, 315, 150),
        ]
        self.buttons = [
            pygame.Rect(385, 520, 210, 66),
            pygame.Rect(615, 520, 190, 66),
            pygame.Rect(825, 520, 170, 66),
        ]

    def on_enter(self):
        """Refresh data when the screen becomes active."""
        return

    def handle_events(self, events):
        """Handle clicks, keyboard shortcuts, and alternative selections."""
        rects = self.cards + self.buttons
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command in {"select", "yes"} and self.app.switch_mode.get_selected_index() is not None:
            selected = self.app.switch_mode.get_selected_index()
        if selected is None:
            return
        if selected < 3:
            self.app.set_input_mode(INPUT_MODES[selected])
            self.app.set_screen("calibration")
        elif selected == 3:
            self.app.set_screen("profile")
        elif selected == 4:
            self.app.set_screen("hub")
        elif selected == 5:
            self.app.set_screen("stats")

    def update(self, elapsed):
        """Update the animated background dots."""
        self.elapsed = pygame.time.get_ticks() / 1000

    def draw(self, surface):
        """Draw the complete home screen."""
        draw_background(surface, self.app.dots, self.elapsed)
        title_font = load_font(FONT_SIZES["title"], True)
        head_font = load_font(34, True)
        draw_text(surface, "AccessPlay", (SCREEN_WIDTH // 2, 120), title_font, CYAN, center=True)
        draw_text(surface, "Play Without Limits", (SCREEN_WIDTH // 2, 196), head_font, WHITE, center=True)
        descriptions = [
            "Move a glowing cursor with head motion",
            "Speak simple commands during games",
            "Scan and select using one keyboard key",
        ]
        for index, rect in enumerate(self.cards):
            selected = self.app.profile.get("input_mode") == INPUT_MODES[index]
            draw_card(surface, rect, INPUT_MODES[index], descriptions[index], CYAN if index != 1 else PURPLE, selected)
        mouse = pygame.mouse.get_pos()
        labels = ["Set Up Profile", "Game Hub", "Stats"]
        for rect, label in zip(self.buttons, labels):
            draw_button(surface, rect, label, CYAN, rect.collidepoint(mouse))
        if self.app.profile.get("input_mode") == "Single Key Mode":
            index = self.app.switch_mode.get_selected_index()
            rects = self.cards + self.buttons
            if index is not None and index < len(rects):
                pygame.draw.rect(surface, CYAN, rects[index].inflate(12, 12), 4, border_radius=16)
        draw_text(surface, "Pygame accessibility demo for Class 12 capstone", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 54), load_font(20), MUTED, center=True)
