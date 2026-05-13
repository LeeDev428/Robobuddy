from dataclasses import dataclass

import cv2
import torch
from ultralytics import YOLO


@dataclass
class DetectionResult:
    person_detected: bool
    confidence: float


class PersonDetector:
    """YOLOv8 person detection with optional preview window."""

    def __init__(self, model_name: str = "yolov8n.pt", camera_index: int = 0, threshold: float = 0.45) -> None:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[VISION] Using device: {self._device.upper()} {'(GTX 1650 active)' if self._device == 'cuda' else '(No GPU — CPU fallback)'}")
        self._model = YOLO(model_name)
        self._model.to(self._device)
        self._threshold = threshold

        # Keep camera open for the lifetime of this detector to avoid per-frame open/close lag
        self._cap = cv2.VideoCapture(camera_index)
        if not self._cap.isOpened():
            raise RuntimeError("Could not open webcam. Check CAMERA_INDEX and camera permissions.")
        # Reduce internal buffer so we always get the latest frame, not a stale one
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def detect_once(self, show_preview: bool = True) -> DetectionResult:
        ok, frame = self._cap.read()
        if not ok:
            return DetectionResult(False, 0.0)

        result = self._model(frame, verbose=False, device=self._device)[0]
        best_conf = 0.0
        person_found = False

        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            if cls_id == 0 and conf >= self._threshold:
                person_found = True
                best_conf = max(best_conf, conf)

        if show_preview:
            label = f"Person: {person_found} ({best_conf:.2f})"
            cv2.putText(frame, label, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("RoboBuddy Vision", frame)
            cv2.waitKey(1)

        return DetectionResult(person_found, best_conf)

    def close_preview(self) -> None:
        if self._cap.isOpened():
            self._cap.release()
        cv2.destroyAllWindows()
