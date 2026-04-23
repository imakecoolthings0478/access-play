"""Starts AccessPlay and keeps the main Pygame loop running."""

import random
import sys

import pygame

from input_modes.head_tracker import HeadTracker
from input_modes.switch_mode import SwitchMode
from input_modes.voice_control import VoiceControl
from screens.calibration import CalibrationScreen
from screens.game_hub import GameHubScreen
from screens.home import HomeScreen
from screens.profile import ProfileScreen
from screens.settings_screen import SettingsScreen
from screens.stats import StatsScreen
from settings import BACKGROUND, CYAN, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from utils.save_manager import load_profile, save_settings
from utils.ui_components import draw_toast


class AccessPlayApp:
    """Central app object shared by every screen.

    The screens stay small by asking this class for navigation, saved profile
    settings, and whichever input mode is currently active.
    """

    def __init__(self):
        """Set up Pygame, load saved preferences, and build the screens."""
        pygame.init()
        pygame.display.set_caption("AccessPlay")
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.profile = load_profile()
        self.toast = ""
        self.toast_timer = 0
        self.dots = [
            [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)]
            for _ in range(90)
        ]
        self.head_tracker = HeadTracker(self.profile.get("dwell_time", 1.5))
        self.voice_control = VoiceControl()
        self.switch_mode = SwitchMode(scan_speed=self.profile.get("scan_speed", 1.5))
        self.screens = {
            "home": HomeScreen(self),
            "profile": ProfileScreen(self),
            "calibration": CalibrationScreen(self),
            "hub": GameHubScreen(self),
            "stats": StatsScreen(self),
            "settings": SettingsScreen(self),
        }
        self.current_screen = self.screens["home"]

    def show_toast(self, message, seconds=2.5):
        """Show a short status message near the top of the window."""
        self.toast = message
        self.toast_timer = seconds

    def set_screen(self, name):
        """Move to another screen and let it refresh its own data."""
        self.current_screen = self.screens[name]
        self.current_screen.on_enter()

    def set_input_mode(self, mode):
        """Save the selected input mode and start its background service."""
        self.profile["input_mode"] = mode
        save_settings({"input_mode": mode})
        if mode == "Head Tracking":
            self.head_tracker.start()
        elif mode == "Voice Control":
            self.voice_control.start()

    def get_action(self, events, rects):
        """Convert the active input mode into a simple selected index/command pair."""
        mode = self.profile.get("input_mode", "Single Key Mode")
        if mode == "Head Tracking":
            if self.head_tracker.error:
                self.profile["input_mode"] = "Single Key Mode"
                self.show_toast(self.head_tracker.error)
            selected = self.head_tracker.is_dwelling(rects)
            return selected, None
        if mode == "Voice Control":
            if self.voice_control.error:
                self.profile["input_mode"] = "Single Key Mode"
                self.show_toast(self.voice_control.error)
            return None, self.voice_control.get_latest_command()
        self.switch_mode.scan_speed = self.profile.get("scan_speed", 1.5)
        self.switch_mode.set_scannable_elements(rects)
        return self.switch_mode.update(events), None

    def draw_access_cursor(self):
        """Draw the head cursor and the small webcam preview during tracking."""
        if self.profile.get("input_mode") != "Head Tracking":
            return
        pos = self.head_tracker.get_cursor_position()
        pygame.draw.circle(self.surface, CYAN, pos, 20, width=3)
        pygame.draw.circle(self.surface, CYAN, pos, 5)
        if self.head_tracker.preview_surface:
            preview_pos = (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 95)
            self.surface.blit(self.head_tracker.preview_surface, preview_pos)

    def run(self):
        """Run one frame at a time until the window is closed."""
        running = True
        while running:
            elapsed = self.clock.tick(FPS) / 1000
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            self.surface.fill(BACKGROUND)
            self.current_screen.handle_events(events)
            self.current_screen.update(elapsed)
            self.current_screen.draw(self.surface)
            self.draw_access_cursor()
            self.toast_timer = max(0, self.toast_timer - elapsed)
            draw_toast(self.surface, self.toast, self.toast_timer)
            pygame.display.flip()
        self.head_tracker.stop()
        self.voice_control.stop()
        pygame.quit()
        sys.exit()


def main():
    """Launch the application."""
    AccessPlayApp().run()


if __name__ == "__main__":
    main()
