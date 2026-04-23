"""Settings screen for accessibility preferences."""

import pygame

from settings import CURSOR_SIZES, CYAN, FONT_SIZES, GREEN, INPUT_MODES, MUTED, PURPLE, RED, WHITE
from utils.save_manager import load_profile, save_settings
from utils.ui_components import draw_background, draw_button, draw_slider, draw_text, load_font


class SettingsScreen:
    """Lets the user adjust input, timing, contrast, sound, and cursor size."""

    def __init__(self, app):
        """Create settings controls."""
        self.app = app
        self.profile = load_profile()
        self.back_rect = pygame.Rect(80, 635, 150, 66)
        self.save_rect = pygame.Rect(250, 635, 160, 66)
        self.mode_rects = [pygame.Rect(90 + i * 340, 155, 300, 66) for i in range(3)]
        self.dwell_slider = pygame.Rect(250, 295, 390, 18)
        self.scan_slider = pygame.Rect(250, 385, 390, 18)
        self.font_rects = [pygame.Rect(735, 270 + i * 80, 245, 62) for i in range(3)]
        self.toggle_rect = pygame.Rect(250, 465, 90, 54)
        self.sound_rect = pygame.Rect(250, 540, 90, 54)
        self.cursor_rects = [pygame.Rect(735 + i * 135, 535, 120, 62) for i in range(3)]

    def on_enter(self):
        """Reload settings from disk."""
        self.profile = load_profile()

    def handle_events(self, events):
        """Handle mouse and alternative selections."""
        rects = [self.back_rect, self.save_rect] + self.mode_rects + self.font_rects + [self.toggle_rect, self.sound_rect] + self.cursor_rects
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command in {"select", "yes"}:
            selected = self.app.switch_mode.get_selected_index()
        if selected == 0:
            self.app.set_screen("hub")
        elif selected == 1:
            self._save()
        elif selected is not None and 2 <= selected < 5:
            self.profile["input_mode"] = INPUT_MODES[selected - 2]
        elif selected is not None and 5 <= selected < 8:
            self.profile["font_size"] = ["Normal", "Large", "Extra Large"][selected - 5]
        elif selected == 8:
            self.profile["high_contrast"] = not self.profile.get("high_contrast", False)
        elif selected == 9:
            self.profile["sound"] = not self.profile.get("sound", True)
        elif selected is not None and 10 <= selected < 13:
            self.profile["cursor_size"] = list(CURSOR_SIZES.keys())[selected - 10]

    def update(self, elapsed):
        """Settings are updated while drawing sliders."""
        return

    def draw(self, surface):
        """Draw settings controls."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Settings", (80, 72), load_font(FONT_SIZES["heading"], True), CYAN)
        mouse = pygame.mouse.get_pos()
        for index, rect in enumerate(self.mode_rects):
            chosen = self.profile.get("input_mode") == INPUT_MODES[index]
            draw_button(surface, rect, INPUT_MODES[index], CYAN if chosen else PURPLE, rect.collidepoint(mouse) or chosen)
        draw_text(surface, "Dwell time", (90, 280), load_font(23), WHITE)
        self.profile["dwell_time"] = round(draw_slider(surface, self.dwell_slider, 0.5, 3.0, self.profile.get("dwell_time", 1.5), self.dwell_slider.inflate(20, 28).collidepoint(mouse)), 1)
        draw_text(surface, f"{self.profile['dwell_time']}s", (665, 280), load_font(22), MUTED)
        draw_text(surface, "Scan speed", (90, 370), load_font(23), WHITE)
        self.profile["scan_speed"] = round(draw_slider(surface, self.scan_slider, 0.5, 3.0, self.profile.get("scan_speed", 1.5), self.scan_slider.inflate(20, 28).collidepoint(mouse)), 1)
        draw_text(surface, f"{self.profile['scan_speed']}s", (665, 370), load_font(22), MUTED)
        self._draw_toggle(surface, self.toggle_rect, "High contrast", self.profile.get("high_contrast", False))
        self._draw_toggle(surface, self.sound_rect, "Sound effects", self.profile.get("sound", True))
        draw_text(surface, "Font size", (735, 238), load_font(23), WHITE)
        for index, rect in enumerate(self.font_rects):
            label = ["Normal", "Large", "Extra Large"][index]
            draw_button(surface, rect, label, GREEN if self.profile.get("font_size") == label else PURPLE, rect.collidepoint(mouse))
        draw_text(surface, "Cursor size", (735, 500), load_font(23), WHITE)
        for index, rect in enumerate(self.cursor_rects):
            label = list(CURSOR_SIZES.keys())[index]
            draw_button(surface, rect, label, GREEN if self.profile.get("cursor_size") == label else PURPLE, rect.collidepoint(mouse))
        draw_button(surface, self.back_rect, "Back", RED, self.back_rect.collidepoint(mouse))
        draw_button(surface, self.save_rect, "Save", GREEN, self.save_rect.collidepoint(mouse))

    def _draw_toggle(self, surface, rect, label, value):
        """Draw an accessible on/off toggle."""
        draw_text(surface, label, (90, rect.y + 13), load_font(23), WHITE)
        pygame.draw.rect(surface, GREEN if value else PURPLE, rect, border_radius=27)
        x = rect.right - 28 if value else rect.x + 28
        pygame.draw.circle(surface, WHITE, (x, rect.centery), 20)

    def _save(self):
        """Persist settings and apply them to the running app."""
        save_settings(self.profile)
        self.app.profile.update(self.profile)
        self.app.switch_mode.scan_speed = self.profile.get("scan_speed", 1.5)
        self.app.head_tracker.dwell.dwell_time = self.profile.get("dwell_time", 1.5)
        self.app.set_input_mode(self.profile.get("input_mode", "Single Key Mode"))
        self.app.show_toast("Settings saved")
