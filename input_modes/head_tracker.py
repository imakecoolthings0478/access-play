"""Webcam head-tracking input mode using OpenCV and MediaPipe when available."""

import threading

import pygame

from settings import DEFAULT_DWELL_TIME, SCREEN_HEIGHT, SCREEN_WIDTH
from utils.accessibility import DwellTimer


class HeadTracker:
    """Tracks nose movement and exposes it as a screen cursor."""

    def __init__(self, dwell_time=DEFAULT_DWELL_TIME):
        """Create a head tracker with graceful fallback behavior."""
        self.cursor = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.error = ""
        self.running = False
        self.thread = None
        self.preview_surface = None
        self.dwell = DwellTimer(dwell_time)

    def start(self):
        """Start webcam processing in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop webcam processing."""
        self.running = False

    def _camera_loop(self):
        """Read webcam frames and map the nose landmark to screen coordinates."""
        try:
            import cv2
            import mediapipe as mp
        except ImportError:
            self.error = "Webcam tracking libraries missing. Switched to Single Key Mode."
            self.running = False
            return
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            self.error = "Webcam not found or permission denied. Use Single Key Mode."
            self.running = False
            return
        face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)
        while self.running:
            ok, frame = camera.read()
            if not ok:
                continue
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)
            if result.multi_face_landmarks:
                nose = result.multi_face_landmarks[0].landmark[1]
                self.cursor[0] = int(max(0, min(SCREEN_WIDTH, nose.x * SCREEN_WIDTH)))
                self.cursor[1] = int(max(0, min(SCREEN_HEIGHT, nose.y * SCREEN_HEIGHT)))
                for point in result.multi_face_landmarks[0].landmark[::25]:
                    x = int(point.x * frame.shape[1])
                    y = int(point.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)
            small = cv2.resize(frame, (100, 75))
            small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            self.preview_surface = pygame.image.frombuffer(small.tobytes(), (100, 75), "RGB")
        camera.release()

    def get_cursor_position(self):
        """Return the current alternative cursor position."""
        return tuple(self.cursor)

    def is_dwelling(self, button_rects):
        """Return the index of a rectangle after a completed dwell click."""
        return self.dwell.update(self.get_cursor_position(), button_rects)
