import pyttsx3


class TextToSpeech:
    """Simple offline text-to-speech wrapper."""

    def __init__(self, rate: int = 170, volume: float = 1.0) -> None:
        self._rate = rate
        self._volume = volume

    def speak(self, text: str) -> None:
        # Reinitialize per call — avoids pyttsx3 engine stall on Windows
        engine = pyttsx3.init()
        engine.setProperty("rate", self._rate)
        engine.setProperty("volume", self._volume)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
