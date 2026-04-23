"""Background voice command input mode."""

import threading

from settings import VOICE_COMMANDS


class VoiceControl:
    """Listens for simple game commands without blocking the Pygame loop."""

    def __init__(self):
        """Create a voice recognizer and delay heavy imports until needed."""
        self.latest_command = None
        self.command_log = []
        self.error = ""
        self.running = False
        self.thread = None

    def start(self):
        """Start microphone recognition in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the listener loop."""
        self.running = False

    def _listen_loop(self):
        """Continuously listen for allowed commands using SpeechRecognition."""
        try:
            import speech_recognition as sr
        except ImportError:
            self.error = "SpeechRecognition is not installed. Use Single Key Mode."
            self.running = False
            return
        recognizer = sr.Recognizer()
        try:
            microphone = sr.Microphone()
        except OSError:
            self.error = "Microphone not found. Try Single Key Mode."
            self.running = False
            return
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
        while self.running:
            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                phrase = recognizer.recognize_google(audio).lower().strip()
                if phrase in VOICE_COMMANDS:
                    self.latest_command = phrase
                    self.command_log.append(phrase)
                    self.command_log = self.command_log[-5:]
            except Exception:
                continue

    def get_latest_command(self):
        """Return and clear the newest recognized command."""
        command = self.latest_command
        self.latest_command = None
        return command

    def get_log(self):
        """Return the five most recent accepted commands."""
        return list(self.command_log)
