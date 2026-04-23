"""Maze Runner game."""

import random
import time

import pygame

from settings import CYAN, FONT_SIZES, GREEN, PURPLE, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from utils.save_manager import add_achievement, clear_paused_game, record_game_play, save_paused_game, save_score
from utils.ui_components import draw_background, draw_button, draw_text, load_font


class MazeRunner:
    """A generated maze where the player moves a glowing circle to the exit."""

    def __init__(self, app):
        """Create maze state."""
        self.app = app
        self.level = 1
        self.paused = False
        self.won = False
        self.back_rect = pygame.Rect(70, 660, 140, 62)
        self.next_rect = pygame.Rect(940, 660, 190, 62)
        self.new_maze()

    def on_enter(self):
        """Prepare the game when launched."""
        return

    def new_maze(self):
        """Generate a recursive-backtracking maze for the current level."""
        self.cols = 10 + self.level * 2
        self.rows = 8 + self.level
        self.cell = min(42, (SCREEN_HEIGHT - 180) // self.rows, (SCREEN_WIDTH - 180) // self.cols)
        self.origin = (80, 120)
        self.grid = [[{"visited": False, "walls": [True, True, True, True]} for _ in range(self.cols)] for _ in range(self.rows)]
        self._carve(0, 0)
        self.player = [0, 0]
        self.start_time = time.time()
        self.won = False

    def _carve(self, x, y):
        """Carve passages through the maze using depth-first recursion."""
        self.grid[y][x]["visited"] = True
        directions = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]
        random.shuffle(directions)
        for dx, dy, wall, opposite in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows and not self.grid[ny][nx]["visited"]:
                self.grid[y][x]["walls"][wall] = False
                self.grid[ny][nx]["walls"][opposite] = False
                self._carve(nx, ny)

    def handle_events(self, events):
        """Handle movement, pause, and navigation."""
        rects = [self.back_rect, self.next_rect]
        selected, command = self.app.get_action(events, rects)
        direction = command
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self._toggle_pause()
                keys = {pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_LEFT: "left", pygame.K_RIGHT: "right"}
                direction = keys.get(event.key, direction)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected = next((i for i, rect in enumerate(rects) if rect.collidepoint(mouse)), selected)
        if command == "pause":
            self._toggle_pause()
        if selected == 0:
            self.app.set_screen("hub")
        elif selected == 1 and self.won:
            self.level = min(5, self.level + 1)
            self.new_maze()
        if not self.paused and not self.won:
            self._move(direction)

    def _move(self, direction):
        """Move the player if the maze wall allows it."""
        if direction not in {"up", "down", "left", "right"}:
            return
        x, y = self.player
        walls = self.grid[y][x]["walls"]
        if direction == "up" and not walls[0]:
            y -= 1
        elif direction == "right" and not walls[1]:
            x += 1
        elif direction == "down" and not walls[2]:
            y += 1
        elif direction == "left" and not walls[3]:
            x -= 1
        self.player = [x, y]
        if x == self.cols - 1 and y == self.rows - 1:
            self._win()

    def _win(self):
        """Save score and mark the maze as completed."""
        self.won = True
        elapsed = time.time() - self.start_time
        save_score("maze_runner", time_taken=elapsed)
        record_game_play(elapsed)
        add_achievement("First Win")
        if elapsed < 30:
            add_achievement("Speed Demon")
        clear_paused_game()

    def _toggle_pause(self):
        """Pause or resume and store progress when paused."""
        self.paused = not self.paused
        if self.paused:
            save_paused_game("maze_runner", {"level": self.level, "player": self.player})

    def update(self, elapsed):
        """Maze Runner updates only from input."""
        return

    def draw(self, surface):
        """Draw the maze, player, timer, and pause/win state."""
        draw_background(surface, self.app.dots, pygame.time.get_ticks() / 1000)
        draw_text(surface, f"Maze Runner - Level {self.level}", (70, 48), load_font(FONT_SIZES["heading"], True), CYAN)
        elapsed = time.time() - self.start_time
        draw_text(surface, f"Time: {elapsed:.1f}s", (850, 58), load_font(26), WHITE)
        ox, oy = self.origin
        for y in range(self.rows):
            for x in range(self.cols):
                px, py = ox + x * self.cell, oy + y * self.cell
                walls = self.grid[y][x]["walls"]
                if walls[0]:
                    pygame.draw.line(surface, PURPLE, (px, py), (px + self.cell, py), 3)
                if walls[1]:
                    pygame.draw.line(surface, PURPLE, (px + self.cell, py), (px + self.cell, py + self.cell), 3)
                if walls[2]:
                    pygame.draw.line(surface, PURPLE, (px, py + self.cell), (px + self.cell, py + self.cell), 3)
                if walls[3]:
                    pygame.draw.line(surface, PURPLE, (px, py), (px, py + self.cell), 3)
        pygame.draw.rect(surface, GREEN, (ox + (self.cols - 1) * self.cell + 8, oy + (self.rows - 1) * self.cell + 8, self.cell - 16, self.cell - 16), border_radius=8)
        cx = ox + self.player[0] * self.cell + self.cell // 2
        cy = oy + self.player[1] * self.cell + self.cell // 2
        pygame.draw.circle(surface, CYAN, (cx, cy), self.cell // 3)
        mouse = pygame.mouse.get_pos()
        draw_button(surface, self.back_rect, "Hub", RED, self.back_rect.collidepoint(mouse))
        if self.won:
            draw_text(surface, "You escaped!", (SCREEN_WIDTH // 2, 640), load_font(32, True), GREEN, center=True)
            draw_button(surface, self.next_rect, "Next Level", GREEN, self.next_rect.collidepoint(mouse))
        elif self.paused:
            draw_text(surface, "Paused - press P to resume", (SCREEN_WIDTH // 2, 650), load_font(30, True), WHITE, center=True)
