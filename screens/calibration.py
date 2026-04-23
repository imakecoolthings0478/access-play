"""Input calibration screen."""

import math

import pygame

from settings import CYAN, FONT_SIZES, GREEN, INPUT_MODES, MUTED, PURPLE, SCREEN_WIDTH, WHITE
from utils.ui_components import draw_background, draw_button, draw_progress_bar, draw_text, load_font


class CalibrationScreen:
    """Shows setup flows for head, voice, and single-key input."""

    def __init__(self, app):
        """Create calibration state."""
        self.app = app
        self.back_rect = pygame.Rect(80, 630, 150, 66)
        self.continue_rect = pygame.Rect(940, 630, 180, 66)
        self.key_rect = pygame.Rect(440, 500, 320, 70)
        self.dot_index = 0
        self.hold_time = 0
        self.points = [(300 + x * 300, 190 + y * 145) for y in range(3) for x in range(3)]

    def on_enter(self):
        """Reset calibration progress and start services if needed."""
        self.dot_index = 0
        self.hold_time = 0
        mode = self.app.profile.get("input_mode")
        if mode == "Head Tracking":
            self.app.head_tracker.start()
        if mode == "Voice Control":
            self.app.voice_control.start()

    def handle_events(self, events):
        """Handle calibration navigation and key picking."""
        rects = [self.back_rect, self.continue_rect, self.key_rect]
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
            if event.type == pygame.KEYDOWN and self.app.profile.get("input_mode") == "Single Key Mode":
                self.app.switch_mode.key = event.key
                self.app.show_toast(f"Control key set to {pygame.key.name(event.key)}")
        if command in {"select", "yes"}:
            selected = 1
        if selected == 0:
            self.app.set_screen("home")
        elif selected == 1:
            self.app.set_screen("hub")

    def update(self, elapsed):
        """Advance the head-tracking dot hold timer."""
        if self.app.profile.get("input_mode") == "Head Tracking" and self.dot_index < len(self.points):
            cursor = self.app.head_tracker.get_cursor_position()
            target = self.points[self.dot_index]
            if math.dist(cursor, target) < 70:
                self.hold_time += elapsed
                if self.hold_time >= 2:
                    self.dot_index += 1
                    self.hold_time = 0
            else:
                self.hold_time = 0

    def draw(self, surface):
        """Draw the correct calibration flow for the active input mode."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        mode = self.app.profile.get("input_mode", INPUT_MODES[2])
        draw_text(surface, f"Calibration: {mode}", (80, 72), load_font(FONT_SIZES["heading"], True), CYAN)
        if mode == "Head Tracking":
            self._draw_head(surface)
        elif mode == "Voice Control":
            self._draw_voice(surface)
        else:
            self._draw_switch(surface)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Back", PURPLE, self.back_rect.collidepoint(mouse))
        draw_button(surface, self.continue_rect, "Continue", GREEN, self.continue_rect.collidepoint(mouse))

    def _draw_head(self, surface):
        """Draw the nine-dot head calibration process."""
        draw_text(surface, "Look at each glowing dot for 2 seconds.", (80, 135), load_font(25), WHITE)
        for index, point in enumerate(self.points):
            color = GREEN if index < self.dot_index else MUTED
            radius = 16 if index != self.dot_index else 26
            pygame.draw.circle(surface, color, point, radius, width=4)
        if self.dot_index < len(self.points):
            pygame.draw.circle(surface, CYAN, self.points[self.dot_index], 12)
            draw_progress_bar(surface, pygame.Rect(410, 610, 380, 18), self.hold_time, 2, CYAN)
        else:
            draw_text(surface, "Calibration complete. Your head now controls the cursor.", (80, 570), load_font(24), GREEN)
        if self.app.head_tracker.error:
            draw_text(surface, self.app.head_tracker.error, (80, 570), load_font(23), GREEN)

    def _draw_voice(self, surface):
        """Draw animated sound bars and recent voice commands."""
        draw_text(surface, "Say: up, down, left, right, fire, select, or pause.", (80, 145), load_font(25), WHITE)
        now = pygame.time.get_ticks() / 250
        for index in range(32):
            height = 40 + math.sin(now + index * 0.55) * 36
            x = 160 + index * 24
            pygame.draw.rect(surface, CYAN, (x, 320 - height / 2, 10, height), border_radius=5)
        draw_text(surface, "Recent commands", (820, 180), load_font(25, True), PURPLE)
        for index, command in enumerate(self.app.voice_control.get_log()):
            draw_text(surface, command, (840, 230 + index * 44), load_font(24), WHITE)
        if self.app.voice_control.error:
            draw_text(surface, self.app.voice_control.error, (80, 570), load_font(23), GREEN)

    def _draw_switch(self, surface):
        """Draw the single-key setup screen."""
        draw_text(surface, "Press the key you want to use for scanning.", (80, 145), load_font(25), WHITE)
        draw_text(surface, "Current key", (SCREEN_WIDTH // 2, 390), load_font(25), MUTED, center=True)
        pygame.draw.rect(surface, (26, 36, 60), self.key_rect, border_radius=14)
        pygame.draw.rect(surface, CYAN, self.key_rect, 4, border_radius=14)
        draw_text(surface, pygame.key.name(self.app.switch_mode.key).upper(), self.key_rect.center, load_font(30, True), WHITE, center=True)
