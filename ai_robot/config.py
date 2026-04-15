import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are RoboBuddy, a friendly educational AI companion robot.",
    )

    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    listen_timeout_sec: int = int(os.getenv("LISTEN_TIMEOUT_SEC", "6"))
    phrase_time_limit_sec: int = int(os.getenv("PHRASE_TIME_LIMIT_SEC", "10"))

    yolo_model: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
    person_confidence: float = float(os.getenv("PERSON_CONFIDENCE", "0.45"))

    robot_host: str = os.getenv("ROBOT_HOST", "192.168.1.50")
    robot_port: int = int(os.getenv("ROBOT_PORT", "5000"))
    socket_timeout_sec: float = float(os.getenv("SOCKET_TIMEOUT_SEC", "2.0"))

    tts_rate: int = int(os.getenv("TTS_RATE", "170"))
    tts_volume: float = float(os.getenv("TTS_VOLUME", "1.0"))


def load_settings() -> Settings:
    """Return settings loaded from the current environment."""
    return Settings()


# Data storage paths (laptop-side for logging detection + conversation history)
DATA_DIR = os.getenv("ROBOBUDDY_DATA_DIR", "./robobuddy_data")
DETECTION_LOG_DIR = os.path.join(DATA_DIR, "detections")
CONVERSATION_LOG_DIR = os.path.join(DATA_DIR, "conversations")
MODEL_CACHE_DIR = os.path.join(DATA_DIR, "models")

# Ensure directories exist
for dir_path in [DATA_DIR, DETECTION_LOG_DIR, CONVERSATION_LOG_DIR, MODEL_CACHE_DIR]:
    os.makedirs(dir_path, exist_ok=True)
