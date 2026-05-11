import os
import subprocess
import sys
import tempfile
import threading
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame


class TextToSpeech:
    """Neural text-to-speech using Microsoft edge-tts + pygame playback.
    Supports stop() to interrupt mid-speech (for user interruptions).
    """

    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
        volume: float = 1.0,
        rate: str = "+22%",
        pitch: str = "+45Hz",
    ) -> None:
        self._voice = voice
        self._volume = min(max(volume, 0.0), 1.0)
        self._rate = rate
        self._pitch = pitch
        self._stop_flag = threading.Event()
        pygame.mixer.init()

    def speak(self, text: str) -> None:
        """Speak text. Blocks until done or stop() is called."""
        self._stop_flag.clear()

        # Generate audio bytes via edge-tts
        audio_data = self._generate_sync(text)
        if not audio_data or self._stop_flag.is_set():
            return

        # Write to temp file (pygame.mixer.music requires a file path for mp3)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                tmp_path = f.name

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()

            max_playback_sec = max(8.0, min(45.0, (len(text) / 14.0) * 1.2 + 3.0))
            deadline = time.monotonic() + max_playback_sec
            while pygame.mixer.music.get_busy():
                if self._stop_flag.is_set():
                    pygame.mixer.music.stop()
                    break
                if time.monotonic() >= deadline:
                    pygame.mixer.music.stop()
                    break
                pygame.time.wait(50)
        finally:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def stop(self) -> None:
        """Interrupt any currently playing speech immediately."""
        self._stop_flag.set()
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def _generate_sync(self, text: str) -> bytes:
        """Generate MP3 bytes via edge-tts CLI (stable on Windows event loops)."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as out_file:
            out_path = out_file.name

        try:
            cmd = [
                sys.executable,
                "-m",
                "edge_tts",
                "--voice",
                self._voice,
                "--rate",
                self._rate,
                "--pitch",
                self._pitch,
                "--text",
                text,
                "--write-media",
                out_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            with open(out_path, "rb") as f:
                return f.read()
        except Exception:
            return b""
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass

