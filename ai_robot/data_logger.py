import json
from datetime import datetime
from pathlib import Path

from ai_robot.config import CONVERSATION_LOG_DIR, DETECTION_LOG_DIR


class DataLogger:
    """Logs detection events and conversation history to disk for future ML training."""

    def __init__(self) -> None:
        self.detection_log = Path(DETECTION_LOG_DIR) / self._get_date_filename("detections")
        self.conversation_log = Path(CONVERSATION_LOG_DIR) / self._get_date_filename("conversations")

    @staticmethod
    def _get_date_filename(prefix: str) -> str:
        """Generate filename with today's date."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{prefix}_{date_str}.jsonl"

    def log_detection(self, person_detected: bool, confidence: float, location: str = "unknown") -> None:
        """Log a person detection event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "person_detected": person_detected,
            "confidence": round(confidence, 4),
            "location": location,
        }
        self._append_to_file(self.detection_log, event)

    def log_conversation(
        self,
        user_input: str,
        ai_response: str,
        model_used: str,
        person_present: bool | None = None,
    ) -> None:
        """Log a conversation exchange."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "model_used": model_used,
            "person_detected": person_present,
        }
        self._append_to_file(self.conversation_log, event)

    @staticmethod
    def _append_to_file(filepath: Path, data: dict) -> None:
        """Append JSON line to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
