import tempfile
import os

import speech_recognition as sr
import whisper


class WhisperSpeechRecognizer:
    """Captures microphone input and transcribes with local Whisper."""

    def __init__(self, model_name: str = "base") -> None:
        self._recognizer = sr.Recognizer()
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.pause_threshold = 0.6
        self._recognizer.non_speaking_duration = 0.35
        self._recognizer.phrase_threshold = 0.2
        self._model = whisper.load_model(model_name)

    @staticmethod
    def _is_valid_text(text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False

        alpha_count = sum(1 for ch in stripped if ch.isalpha())
        if alpha_count < 2:
            return False

        # Avoid obvious punctuation/noise artifacts.
        if stripped in {".", "..", "...", "?", "!?", "-", "_"}:
            return False

        return True

    def listen_and_transcribe(
        self,
        timeout_sec: int = 6,
        phrase_time_limit_sec: int = 10,
    ) -> str | None:
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.6)
            self._recognizer.energy_threshold = max(300, self._recognizer.energy_threshold * 1.35)
            audio = self._recognizer.listen(
                source,
                timeout=timeout_sec,
                phrase_time_limit=phrase_time_limit_sec,
            )

        wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name

        try:
            result = self._model.transcribe(
                tmp_path,
                language="en",
                fp16=False,
                temperature=0.0,
                condition_on_previous_text=False,
                no_speech_threshold=0.7,
            )

            segments = result.get("segments") or []
            if segments:
                all_silent = all(float(seg.get("no_speech_prob", 0.0)) > 0.7 for seg in segments)
                if all_silent:
                    return None

                mean_logprob = sum(float(seg.get("avg_logprob", -1.0)) for seg in segments) / len(segments)
                raw_text = (result.get("text") or "").strip()
                if mean_logprob < -1.0 and len(raw_text) < 8:
                    return None

            text = (result.get("text") or "").strip()
            return text if self._is_valid_text(text) else None
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
