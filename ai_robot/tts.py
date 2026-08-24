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
        self._offline_engine = None
        self._mixer_ready = False
        try:
            pygame.mixer.init()
            self._mixer_ready = True
        except Exception as exc:
            print(f"[TTS] Audio mixer unavailable; using offline voice fallback: {exc}")

    def speak(self, text: str) -> None:
        """Speak text. Blocks until done or stop() is called."""
        self._stop_flag.clear()
        if not self._mixer_ready:
            self._speak_offline(text)
            return

        # Generate audio bytes via edge-tts
        audio_data = self._generate_sync(text)
        if self._stop_flag.is_set():
            return
        if not audio_data:
            self._speak_offline(text)
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
        if self._mixer_ready:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        if self._offline_engine is not None:
            try:
                self._offline_engine.stop()
            except Exception:
                pass

    def _speak_offline(self, text: str) -> None:
        """Use the installed OS voice when edge-tts or pygame is unavailable."""
        try:
            import pyttsx3

            if self._offline_engine is None:
                self._offline_engine = pyttsx3.init()
                self._offline_engine.setProperty("volume", self._volume)
                self._offline_engine.setProperty("rate", 185)
            if not self._stop_flag.is_set():
                self._offline_engine.say(text)
                self._offline_engine.runAndWait()
        except Exception as exc:
            print(f"[TTS] Unable to speak response: {exc}")

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
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=20)

            with open(out_path, "rb") as f:
                return f.read()
        except subprocess.TimeoutExpired:
            print("[TTS] Neural voice timed out; using offline voice fallback.")
            return b""
        except Exception as exc:
            print(f"[TTS] Neural voice unavailable; using offline voice fallback: {exc}")
            return b""
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass

