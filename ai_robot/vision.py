from dataclasses import dataclass

import cv2
from ultralytics import YOLO


@dataclass
class DetectionResult:
    person_detected: bool
    confidence: float


class PersonDetector:
    """YOLOv8 person detection with optional preview window."""

    def __init__(self, model_name: str = "yolov8n.pt", camera_index: int = 0, threshold: float = 0.45) -> None:
        self._model = YOLO(model_name)
        self._camera_index = camera_index
        self._threshold = threshold

    def detect_once(self, show_preview: bool = True) -> DetectionResult:
        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam. Check CAMERA_INDEX and camera permissions.")

        ok, frame = cap.read()
        cap.release()
        if not ok:
            return DetectionResult(False, 0.0)

        result = self._model(frame, verbose=False)[0]
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
        cv2.destroyAllWindows()
