"""Helpers shared by dwell clicking and scanning controls."""

import pygame

from settings import CYAN, DEFAULT_DWELL_TIME


class DwellTimer:
    """Tracks when an alternative cursor has stayed over a target long enough."""

    def __init__(self, dwell_time=DEFAULT_DWELL_TIME):
        """Create a dwell timer with a required hold duration."""
        self.dwell_time = dwell_time
        self.active_rect = None
        self.started_at = 0

    def update(self, cursor_pos, rects):
        """Return the selected rect index when dwelling completes."""
        now = pygame.time.get_ticks() / 1000
        for index, rect in enumerate(rects):
            if rect.collidepoint(cursor_pos):
                if self.active_rect != index:
                    self.active_rect = index
                    self.started_at = now
                if now - self.started_at >= self.dwell_time:
                    self.started_at = now
                    return index
                return None
        self.active_rect = None
        return None


def draw_scan_highlight(surface, rect):
    """Draw a bright focus rectangle around the currently scanned element."""
    pygame.draw.rect(surface, CYAN, rect.inflate(10, 10), width=4, border_radius=14)
