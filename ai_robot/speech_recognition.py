import tempfile

import speech_recognition as sr
import whisper


class WhisperSpeechRecognizer:
    """Captures microphone input and transcribes with local Whisper."""

    def __init__(self, model_name: str = "base") -> None:
        self._recognizer = sr.Recognizer()
        self._model = whisper.load_model(model_name)

    def listen_and_transcribe(
        self,
        timeout_sec: int = 6,
        phrase_time_limit_sec: int = 10,
    ) -> str | None:
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = self._recognizer.listen(
                source,
                timeout=timeout_sec,
                phrase_time_limit=phrase_time_limit_sec,
            )

        wav_bytes = audio.get_wav_data()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name

        result = self._model.transcribe(tmp_path)
        text = (result.get("text") or "").strip()
        return text or None
