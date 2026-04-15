#!/usr/bin/env python3
"""
Raspberry Pi Servo Control Server for RoboBuddy.

Listens for socket commands and controls servo motors via PCA9685 PWM driver.
Run on the Raspberry Pi:
    python pi_servo_server.py

Tested on: Raspberry Pi 4 with PCA9685 I2C breakout + SG90 servos.
"""

import socket
import sys
import time
from typing import Optional

try:
    from adafruit_pca9685 import PCA9685
    from board import I2C
except ImportError:
    print("ERROR: Adafruit libraries not installed.")
    print("Install with: pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-busdevice")
    sys.exit(1)


class ServoController:
    """Controls servo motors via PCA9685 I2C driver."""

    # Servo pulse width range (in microseconds)
    # Typical SG90: 1000 µs (0°) to 2000 µs (180°)
    MIN_PULSE_US = 1000
    MAX_PULSE_US = 2000
    FREQUENCY = 50  # Hz (standard for servos)

    def __init__(self, i2c_address: int = 0x40) -> None:
        """
        Initialize PCA9685 driver.

        Args:
            i2c_address: I2C address of PCA9685 (default 0x40)
        """
        try:
            i2c = I2C()
            self.pca = PCA9685(i2c, address=i2c_address)
            self.pca.frequency = self.FREQUENCY
            print("[SERVO] PCA9685 initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize PCA9685: {e}")
            sys.exit(1)

        # Servo channel assignments
        self.CHANNEL_HEAD_PAN = 0      # Left/Right
        self.CHANNEL_HEAD_TILT = 1     # Up/Down
        self.CHANNEL_ARM_WAVE = 2      # Waving motion

        # Current servo positions (0–180°)
        self._positions = {
            self.CHANNEL_HEAD_PAN: 90,
            self.CHANNEL_HEAD_TILT: 90,
            self.CHANNEL_ARM_WAVE: 0,
        }

        # Initialize all servos to center position
        self.set_servo_position(self.CHANNEL_HEAD_PAN, 90)
        self.set_servo_position(self.CHANNEL_HEAD_TILT, 90)
        self.set_servo_position(self.CHANNEL_ARM_WAVE, 0)
        print("[SERVO] All servos initialized to safe positions")

    def _angle_to_pulse(self, angle: int) -> int:
        """Convert angle (0–180°) to pulse width (in microseconds)."""
        angle = max(0, min(180, angle))  # Clamp to 0–180
        pulse_range = self.MAX_PULSE_US - self.MIN_PULSE_US
        return int(self.MIN_PULSE_US + (angle / 180.0) * pulse_range)

    def _pulse_to_pwm(self, pulse_us: int) -> int:
        """Convert pulse width (µs) to PCA9685 PWM value (0–4095)."""
        cycle_time_us = 1_000_000 / self.FREQUENCY
        return int((pulse_us / cycle_time_us) * 4096)

    def set_servo_position(self, channel: int, angle: int, duration_ms: int = 500) -> None:
        """
        Move servo to target angle with smooth interpolation.

        Args:
            channel: PCA9685 channel (0–15)
            angle: Target angle (0–180°)
            duration_ms: Smooth transition time in milliseconds
        """
        angle = max(0, min(180, angle))
        current_angle = self._positions.get(channel, 90)

        steps = 20
        step_delay = duration_ms / (steps * 1000.0)

        for step in range(steps + 1):
            intermediate_angle = int(current_angle + (angle - current_angle) * (step / steps))
            pulse = self._angle_to_pulse(intermediate_angle)
            pwm_value = self._pulse_to_pwm(pulse)
            self.pca.channels[channel].duty_cycle = pwm_value
            if step < steps:
                time.sleep(step_delay)

        self._positions[channel] = angle
        print(f"[SERVO] Channel {channel} → {angle}°")

    def head_turn_left(self) -> None:
        """Turn head to the left."""
        self.set_servo_position(self.CHANNEL_HEAD_PAN, 30, duration_ms=400)

    def head_turn_right(self) -> None:
        """Turn head to the right."""
        self.set_servo_position(self.CHANNEL_HEAD_PAN, 150, duration_ms=400)

    def head_center(self) -> None:
        """Center head position."""
        self.set_servo_position(self.CHANNEL_HEAD_PAN, 90, duration_ms=300)

    def wave_arm(self) -> None:
        """Wave arm in sequence."""
        positions = [0, 45, 90, 45, 0]
        for pos in positions:
            self.set_servo_position(self.CHANNEL_ARM_WAVE, pos, duration_ms=150)

    def speaking_motion(self) -> None:
        """Quick motion while speaking (head tilt)."""
        original = self._positions[self.CHANNEL_HEAD_TILT]
        self.set_servo_position(self.CHANNEL_HEAD_TILT, max(0, original - 15), duration_ms=100)
        time.sleep(0.15)
        self.set_servo_position(self.CHANNEL_HEAD_TILT, original, duration_ms=100)

    def shutdown(self) -> None:
        """Safe shutdown: return all servos to neutral."""
        print("[SERVO] Shutting down... returning to neutral positions")
        self.set_servo_position(self.CHANNEL_HEAD_PAN, 90, duration_ms=200)
        self.set_servo_position(self.CHANNEL_HEAD_TILT, 90, duration_ms=200)
        self.set_servo_position(self.CHANNEL_ARM_WAVE, 0, duration_ms=200)


class RoboBuddyServer:
    """Socket server that receives motion commands from laptop."""

    COMMANDS = {
        "HEAD_LEFT": "head_turn_left",
        "HEAD_RIGHT": "head_turn_right",
        "HEAD_CENTER": "head_center",
        "WAVE_ARM": "wave_arm",
        "SPEAK_START": "speaking_motion",
        "SPEAK_END": "head_center",
    }

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, servo_controller: Optional[ServoController] = None) -> None:
        """
        Initialize socket server.

        Args:
            host: Bind address (0.0.0.0 = listen on all interfaces)
            port: Listen port
            servo_controller: ServoController instance (creates new if None)
        """
        self.host = host
        self.port = port
        self.servo = servo_controller or ServoController()
        self.running = False

    def handle_command(self, command: str) -> None:
        """Execute command if recognized."""
        command = command.strip().upper()
        if command in self.COMMANDS:
            method_name = self.COMMANDS[command]
            method = getattr(self.servo, method_name)
            method()
            print(f"[CMD] Executed: {command}")
        else:
            print(f"[WARN] Unknown command: {command}")

    def start(self) -> None:
        """Start listening for connections."""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port}")

        try:
            while self.running:
                try:
                    client_socket, client_addr = server_socket.accept()
                    print(f"[CONNECT] Client {client_addr}")

                    while True:
                        data = client_socket.recv(1024).decode("utf-8")
                        if not data:
                            break
                        for line in data.strip().split("\n"):
                            if line:
                                self.handle_command(line)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"[ERROR] {e}")
                finally:
                    client_socket.close()
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received interrupt")
        finally:
            server_socket.close()
            self.servo.shutdown()


def main() -> None:
    """Main entry point."""
    print("=" * 50)
    print("RoboBuddy Raspberry Pi Servo Control Server")
    print("=" * 50)

    servo = ServoController(i2c_address=0x40)
    server = RoboBuddyServer(host="0.0.0.0", port=5000, servo_controller=servo)

    print("\nWaiting for commands from laptop...")
    print("Send commands like: HEAD_LEFT, WAVE_ARM, SPEAK_START")
    print("(Press Ctrl+C to stop)")
    print()

    try:
        server.start()
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
