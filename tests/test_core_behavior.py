import unittest

from ai_robot.main import extract_after_wake_word
from pi_servo_server import ServoController


class CoreBehaviorTests(unittest.TestCase):
    def test_wake_word_extracts_question(self) -> None:
        self.assertEqual(
            extract_after_wake_word("RoboBuddy, what is Jupiter?", "robobuddy"),
            "what is Jupiter",
        )

    def test_servo_pulse_uses_16_bit_adafruit_duty_cycle(self) -> None:
        controller = ServoController.__new__(ServoController)

        self.assertEqual(controller._pulse_to_pwm(1000), 3276)
        self.assertEqual(controller._pulse_to_pwm(2000), 6553)


if __name__ == "__main__":
    unittest.main()
