# AccessPlay

AccessPlay is my Class 12 capstone project: a small desktop gaming platform
for players who may not be able to use a mouse comfortably. The app is made
with Python and Pygame, and the games can be controlled with head tracking,
voice commands, or a single-key scanning mode.

## Setup

```bash
pip install -r requirements.txt
```

If PyAudio fails to install on Windows, install a matching wheel for your
Python version. The rest of the app can still be shown with Single Key Mode.

## Run

```bash
python main.py
```

Run this command from inside the `accessplay` folder.

## Notes

- Head Tracking uses OpenCV and MediaPipe when a webcam is available.
- Voice Control uses SpeechRecognition and Google Speech API, so voice input
  needs internet while commands are being recognized.
- If the webcam or microphone is not available, the app shows a message and
  continues with Single Key Mode.
- Profile, settings, scores, achievements, and paused progress are saved in
  the `data` folder.
