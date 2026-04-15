import pyttsx3


class TextToSpeech:
    """Simple offline text-to-speech wrapper."""

    def __init__(self, rate: int = 170, volume: float = 1.0) -> None:
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)

    def speak(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()
