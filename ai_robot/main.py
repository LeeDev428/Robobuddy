import argparse
import threading
import time

from ai_robot.config import load_settings
from ai_robot.conversation_ai import ConversationAI
from ai_robot.data_logger import DataLogger
from ai_robot.robot_controller import RobotController
from ai_robot.speech_recognition import WhisperSpeechRecognizer
from ai_robot.tts import TextToSpeech
from ai_robot.vision import PersonDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RoboBuddy AI companion robot")
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="1=Talking AI, 2=+Person detection, 3=+Servo movement, 4=Improved full flow",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable OpenCV camera preview window.",
    )
    return parser.parse_args()


def wait_for_person(detector: PersonDetector, preview: bool) -> None:
    print("[VISION] Waiting for a person...")
    while True:
        result = detector.detect_once(show_preview=preview)
        if result.person_detected:
            print(f"[VISION] Person detected (confidence={result.confidence:.2f})")
            return
        time.sleep(0.35)


def speak_interruptible(tts: TextToSpeech, stt: WhisperSpeechRecognizer, text: str, settings) -> str | None:
    """Speak text while listening for user interruption.
    Returns the interruption transcript if the user spoke, else None.
    Works best with headphones (avoids mic picking up speaker output).
    """
    interrupted_text: list[str | None] = [None]
    tts_done = threading.Event()

    def _speak() -> None:
        tts.speak(text)
        tts_done.set()

    def _listen_for_interrupt() -> None:
        time.sleep(0.7)  # Brief pause so TTS starts before we listen
        if tts_done.is_set():
            return
        try:
            result = stt.listen_and_transcribe(
                timeout_sec=settings.listen_timeout_sec,
                phrase_time_limit_sec=settings.phrase_time_limit_sec,
            )
            if result and not tts_done.is_set():
                interrupted_text[0] = result
                tts.stop()
        except Exception:
            pass

    t_speak = threading.Thread(target=_speak, daemon=True)
    t_listen = threading.Thread(target=_listen_for_interrupt, daemon=True)
    t_speak.start()
    t_listen.start()
    t_speak.join(timeout=120)
    tts_done.set()
    t_listen.join(timeout=settings.phrase_time_limit_sec + 3)

    return interrupted_text[0]


def run() -> None:
    args = parse_args()
    settings = load_settings()

    tts = TextToSpeech(voice=settings.tts_voice, volume=settings.tts_volume)
    stt = WhisperSpeechRecognizer(model_name=settings.whisper_model)
    ai = ConversationAI(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        system_prompt=settings.system_prompt,
    )
    logger = DataLogger()

    detector = None
    robot = None

    if args.stage >= 2:
        detector = PersonDetector(
            model_name=settings.yolo_model,
            camera_index=settings.camera_index,
            threshold=settings.person_confidence,
        )

    if args.stage >= 3:
        robot = RobotController(
            host=settings.robot_host,
            port=settings.robot_port,
            timeout_sec=settings.socket_timeout_sec,
        )

    print(f"[BOOT] RoboBuddy started in stage {args.stage}")
    print("[TIP] Say 'exit' or 'quit' to stop.")

    greeted = False
    pending_user_text: str | None = None  # Set when user interrupts AI speech
    try:
        while True:
            if args.stage >= 2 and detector is not None:
                wait_for_person(detector, preview=not args.no_preview)

            # Log person detection
            if detector is not None:
                result = detector.detect_once(show_preview=False)
                logger.log_detection(
                    person_detected=result.person_detected,
                    confidence=result.confidence,
                    location="demo_room"
                )

            if not greeted:
                greeting = "Hello! I am RoboBuddy. Nice to meet you."
                print(f"[TTS] {greeting}")
                if robot is not None:
                    robot.wave_arm()
                interrupt = speak_interruptible(tts, stt, greeting, settings)
                greeted = True
                if interrupt:
                    pending_user_text = interrupt

            # ---- Get user input ----
            if pending_user_text:
                user_text = pending_user_text
                pending_user_text = None
                print(f"[USER-INTERRUPT] {user_text}")
            else:
                print("[STT] Listening...")
                try:
                    user_text = stt.listen_and_transcribe(
                        timeout_sec=settings.listen_timeout_sec,
                        phrase_time_limit_sec=settings.phrase_time_limit_sec,
                    )
                except Exception as exc:
                    print(f"[STT] Could not capture audio: {exc}")
                    continue

                if not user_text:
                    print("[STT] No speech recognized.")
                    continue

                print(f"[USER] {user_text}")

            if user_text.lower() in {"quit", "exit", "stop"}:
                bye = "Goodbye. See you next time!"
                if robot is not None:
                    robot.head_turn_right()
                tts.speak(bye)
                break

            # ---- Ask AI ----
            try:
                ai_text = ai.ask(user_text)
            except Exception as exc:
                ai_text = f"I am having trouble reaching my brain right now. Please try again."
                print(f"[ERROR] {exc}")

            print(f"[AI] {ai_text}")

            # Log conversation
            logger.log_conversation(
                user_input=user_text,
                ai_response=ai_text,
                model_used=settings.groq_model,
                person_present=(detector is not None and result.person_detected) if args.stage >= 2 else None
            )

            if robot is not None:
                robot.speaking_motion()

            # ---- Speak response (interruptible) ----
            interrupt = speak_interruptible(tts, stt, ai_text, settings)
            if interrupt:
                pending_user_text = interrupt

            # Stage 4: require person presence before every interaction cycle.
            if args.stage >= 4:
                greeted = False

    finally:
        if detector is not None:
            detector.close_preview()


if __name__ == "__main__":
    run()
