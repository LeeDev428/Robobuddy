import argparse
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


def run() -> None:
    args = parse_args()
    settings = load_settings()

    tts = TextToSpeech(rate=settings.tts_rate, volume=settings.tts_volume)
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
                tts.speak(greeting)
                greeted = True

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
                bye = "Goodbye. See you next time."
                if robot is not None:
                    robot.head_turn_right()
                tts.speak(bye)
                break

            try:
                ai_text = ai.ask(user_text)
            except Exception as exc:
                ai_text = f"I am having trouble reaching the AI service right now. {exc}"

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
            tts.speak(ai_text)

            # In stage 4, require person presence before every interaction cycle.
            if args.stage >= 4:
                greeted = False

    finally:
        if detector is not None:
            detector.close_preview()


if __name__ == "__main__":
    run()
