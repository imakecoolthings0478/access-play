"""Single-key scanning input mode."""

import pygame

from settings import DEFAULT_SCAN_SPEED


class SwitchMode:
    """Moves focus through elements and selects one with a single key."""

    def __init__(self, key=pygame.K_SPACE, scan_speed=DEFAULT_SCAN_SPEED):
        """Create a scanner with a selected keyboard key."""
        self.key = key
        self.scan_speed = scan_speed
        self.elements = []
        self.index = 0
        self.last_step = 0
        self.selected_index = None

    def set_scannable_elements(self, elements):
        """Receive the current screen's selectable rectangles."""
        self.elements = list(elements)
        if self.elements:
            self.index %= len(self.elements)
        else:
            self.index = 0

    def update(self, events):
        """Advance the scanner and return the selected index if activated."""
        self.selected_index = None
        if not self.elements:
            return None
        now = pygame.time.get_ticks() / 1000
        if now - self.last_step >= self.scan_speed:
            self.index = (self.index + 1) % len(self.elements)
            self.last_step = now
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == self.key:
                self.selected_index = self.index
                return self.index
        return None

    def get_selected_index(self):
        """Return the current highlighted element index."""
        return self.index if self.elements else None
