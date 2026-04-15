import socket


class RobotController:
    """Sends movement commands to a Raspberry Pi socket server."""

    def __init__(self, host: str, port: int, timeout_sec: float = 2.0) -> None:
        self.host = host
        self.port = port
        self.timeout_sec = timeout_sec

    def send_command(self, command: str) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout_sec) as sock:
                sock.sendall((command.strip() + "\n").encode("utf-8"))
            return True
        except OSError:
            return False

    def head_turn_left(self) -> bool:
        return self.send_command("HEAD_LEFT")

    def head_turn_right(self) -> bool:
        return self.send_command("HEAD_RIGHT")

    def wave_arm(self) -> bool:
        return self.send_command("WAVE_ARM")

    def speaking_motion(self) -> None:
        self.send_command("SPEAK_START")
        self.send_command("SPEAK_END")
