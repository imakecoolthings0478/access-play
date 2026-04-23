"""Profile setup screen."""

import pygame

from settings import (
    AVATARS, CYAN, DISABILITY_OPTIONS, FONT_SIZES, GREEN, MUTED, PURPLE,
    RED, WHITE,
)
from utils.save_manager import load_profile, save_profile
from utils.ui_components import draw_background, draw_button, draw_frosted_card, draw_slider, draw_text, load_font


class ProfileScreen:
    """Lets the player set their name and comfort preferences."""

    def __init__(self, app):
        """Store the rectangles used by the form."""
        self.app = app
        self.profile = load_profile()
        self.name_active = False
        self.name_rect = pygame.Rect(150, 180, 420, 66)
        self.save_rect = pygame.Rect(150, 625, 180, 66)
        self.back_rect = pygame.Rect(350, 625, 150, 66)
        self.slider_rect = pygame.Rect(150, 535, 420, 18)
        self.avatar_rects = [pygame.Rect(162 + i * 80, 310, 62, 62) for i in range(6)]
        self.disability_rects = [pygame.Rect(650, 185 + i * 80, 390, 62) for i in range(4)]

    def on_enter(self):
        """Reload the profile from disk."""
        self.profile = load_profile()

    def handle_events(self, events):
        """Handle text input, avatar choice, disability type, and buttons."""
        rects = [self.save_rect, self.back_rect] + self.avatar_rects + self.disability_rects
        selected, command = self.app.get_action(events, rects)
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.name_active = self.name_rect.collidepoint(mouse)
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
            if event.type == pygame.KEYDOWN and self.name_active:
                if event.key == pygame.K_BACKSPACE:
                    self.profile["name"] = self.profile.get("name", "")[:-1]
                elif event.key == pygame.K_RETURN:
                    self.name_active = False
                elif len(event.unicode) == 1 and len(self.profile.get("name", "")) < 18:
                    self.profile["name"] = self.profile.get("name", "") + event.unicode
        if command in {"select", "yes"}:
            selected = self.app.switch_mode.get_selected_index()
        if selected == 0:
            save_profile(self.profile)
            self.app.profile.update(self.profile)
            self.app.show_toast("Profile saved")
        elif selected == 1:
            self.app.set_screen("home")
        elif selected is not None and 2 <= selected < 8:
            self.profile["avatar"] = selected - 2
        elif selected is not None and 8 <= selected < 12:
            self.profile["disability"] = DISABILITY_OPTIONS[selected - 8]

    def update(self, elapsed):
        """Keep the method for the common screen interface."""
        return

    def draw(self, surface):
        """Draw the full profile form."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, "Profile Setup", (150, 76), load_font(FONT_SIZES["heading"], True), CYAN)
        draw_frosted_card(surface, pygame.Rect(110, 140, 500, 460), PURPLE)
        draw_frosted_card(surface, pygame.Rect(620, 140, 470, 460), CYAN)
        draw_text(surface, "Player name", (150, 150), load_font(22), MUTED)
        pygame.draw.rect(surface, (25, 33, 54), self.name_rect, border_radius=12)
        pygame.draw.rect(surface, CYAN if self.name_active else PURPLE, self.name_rect, 3, border_radius=12)
        name = self.profile.get("name")
        draw_text(surface, name or "Type your name", (170, 198), load_font(26), WHITE if name else MUTED)
        draw_text(surface, "Avatar", (150, 276), load_font(22), MUTED)
        for index, rect in enumerate(self.avatar_rects):
            initials, color = AVATARS[index]
            pygame.draw.circle(surface, color, rect.center, 30)
            if self.profile.get("avatar", 0) == index:
                pygame.draw.circle(surface, WHITE, rect.center, 35, 4)
            draw_text(surface, initials, rect.center, load_font(20, True), (7, 11, 20), center=True)
        draw_text(surface, "Input sensitivity", (150, 490), load_font(22), MUTED)
        mouse = pygame.mouse.get_pos()
        if self.slider_rect.inflate(18, 26).collidepoint(mouse):
            new_value = draw_slider(
                surface, self.slider_rect, 1, 10,
                self.profile.get("sensitivity", 5), True,
            )
            self.profile["sensitivity"] = int(round(new_value))
        else:
            draw_slider(surface, self.slider_rect, 1, 10, self.profile.get("sensitivity", 5))
        draw_text(surface, str(self.profile.get("sensitivity", 5)), (590, 518), load_font(24, True), GREEN)
        draw_text(surface, "Disability type", (650, 150), load_font(22), MUTED)
        for index, rect in enumerate(self.disability_rects):
            chosen = self.profile.get("disability") == DISABILITY_OPTIONS[index]
            pygame.draw.rect(surface, (28, 38, 62), rect, border_radius=12)
            pygame.draw.rect(surface, CYAN if chosen else PURPLE, rect, 3, border_radius=12)
            draw_text(surface, DISABILITY_OPTIONS[index], (rect.x + 18, rect.y + 18), load_font(22))
        draw_button(surface, self.save_rect, "Save", GREEN, self.save_rect.collidepoint(mouse))
        draw_button(surface, self.back_rect, "Back", RED, self.back_rect.collidepoint(mouse))
