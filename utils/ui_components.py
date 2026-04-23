"""Reusable drawing helpers.

Pygame does not include a button or card system, so the project keeps those
small drawing routines here instead of repeating the same rectangles on every
screen.
"""

import math

import pygame

from settings import (
    BACKGROUND, BUTTON_MIN_SIZE, CYAN, FONT_DIR, FONT_NAME, FONT_SIZES, MUTED, PANEL,
    PANEL_LIGHT, PURPLE, WHITE,
)


def load_font(size, bold=False):
    """Load the bundled font when available; otherwise use the system fallback."""
    font_files = list(FONT_DIR.glob("*.ttf"))
    if font_files:
        return pygame.font.Font(str(font_files[0]), size)
    return pygame.font.SysFont(FONT_NAME, size, bold=bold)


def draw_text(surface, text, pos, font, color=WHITE, center=False):
    """Draw text on a surface and return its rectangle."""
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)
    return rect


def draw_glow_rect(surface, rect, color=CYAN, radius=14, width=2):
    """Draw a soft border by stacking transparent outlines."""
    for grow, alpha in [(10, 40), (5, 80), (0, 230)]:
        glow = pygame.Surface((rect.width + grow * 2, rect.height + grow * 2), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (*color, alpha),
            glow.get_rect(),
            width=width,
            border_radius=radius + grow,
        )
        surface.blit(glow, (rect.x - grow, rect.y - grow))


def draw_frosted_card(surface, rect, border_color=CYAN):
    """Draw the dark translucent card style used across the app."""
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, (*PANEL, 205), card.get_rect(), border_radius=16)
    pygame.draw.rect(card, (*PANEL_LIGHT, 70), card.get_rect().inflate(-8, -8), border_radius=12)
    surface.blit(card, rect)
    draw_glow_rect(surface, rect, border_color, radius=16)


def draw_button(surface, rect, text, color=CYAN, hover=False, font=None):
    """Draw a large accessible button and report mouse clicks."""
    font = font or load_font(FONT_SIZES["body"], bold=True)
    safe_rect = pygame.Rect(rect)
    safe_rect.width = max(safe_rect.width, BUTTON_MIN_SIZE)
    safe_rect.height = max(safe_rect.height, BUTTON_MIN_SIZE)
    fill = PANEL_LIGHT if hover else PANEL
    pygame.draw.rect(surface, fill, safe_rect, border_radius=14)
    draw_glow_rect(surface, safe_rect, color if hover else PURPLE, radius=14)
    draw_text(surface, text, safe_rect.center, font, WHITE, center=True)
    mouse_down = pygame.mouse.get_pressed()[0]
    return hover and mouse_down


def draw_card(surface, rect, title, description, icon_color, selected=False):
    """Draw an option card with a simple icon and two lines of text."""
    draw_frosted_card(surface, rect, CYAN if selected else PURPLE)
    icon_center = (rect.x + 54, rect.y + 58)
    pygame.draw.circle(surface, icon_color, icon_center, 25, width=4)
    pygame.draw.circle(surface, icon_color, icon_center, 9)
    draw_text(surface, title, (rect.x + 96, rect.y + 28), load_font(25, True))
    draw_text(surface, description, (rect.x + 96, rect.y + 68), load_font(18), MUTED)


def draw_slider(surface, rect, min_val, max_val, current_val, active=False):
    """Draw and update a horizontal slider using the mouse."""
    pygame.draw.rect(surface, PANEL_LIGHT, rect, border_radius=rect.height // 2)
    percent = (current_val - min_val) / (max_val - min_val)
    knob_x = rect.x + int(percent * rect.width)
    pygame.draw.rect(surface, CYAN, (rect.x, rect.y, knob_x - rect.x, rect.height), border_radius=rect.height // 2)
    pygame.draw.circle(surface, WHITE, (knob_x, rect.centery), 16)
    if active and pygame.mouse.get_pressed()[0]:
        mouse_x = max(rect.x, min(pygame.mouse.get_pos()[0], rect.right))
        percent = (mouse_x - rect.x) / rect.width
        return min_val + percent * (max_val - min_val)
    return current_val


def draw_progress_bar(surface, rect, value, max_value, color=CYAN):
    """Draw a clipped progress bar for timers and score meters."""
    pygame.draw.rect(surface, PANEL_LIGHT, rect, border_radius=10)
    width = int(rect.width * max(0, min(value / max_value, 1)))
    pygame.draw.rect(surface, color, (rect.x, rect.y, width, rect.height), border_radius=10)


def draw_toast(surface, message, timer):
    """Draw a temporary notification at the top of the screen."""
    if timer <= 0 or not message:
        return
    font = load_font(22, True)
    rect = pygame.Rect(0, 0, 620, 54)
    rect.center = (surface.get_width() // 2, 42)
    pygame.draw.rect(surface, (24, 34, 54), rect, border_radius=12)
    draw_glow_rect(surface, rect, CYAN, radius=12)
    draw_text(surface, message, rect.center, font, center=True)


def draw_background(surface, dots, elapsed):
    """Draw the dark animated star background."""
    surface.fill(BACKGROUND)
    for index, dot in enumerate(dots):
        dot[1] += 0.15 + (index % 3) * 0.05
        if dot[1] > surface.get_height():
            dot[1] = 0
        pulse = 1 + math.sin(elapsed * 2 + index) * 0.4
        pygame.draw.circle(surface, WHITE, (int(dot[0]), int(dot[1])), max(1, int(2 * pulse)))
