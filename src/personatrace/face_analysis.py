from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.personatrace.video_analysis import FrameSample


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class FaceFrameResult:
    frame_index: int
    timestamp_seconds: float
    faces: list[FaceBox]
    annotated_image_rgb: np.ndarray


@dataclass(frozen=True)
class FaceConsistencyResult:
    total_frames_checked: int
    frames_with_face: int
    frames_with_multiple_faces: int
    detection_rate: float
    center_jitter: float
    size_jitter: float
    risk_score: int
    risk_level: str
    reasons: list[str]
    frame_results: list[FaceFrameResult]


def analyze_face_consistency(samples: list[FrameSample]) -> FaceConsistencyResult:
    detector = _load_face_detector()
    frame_results = [_analyze_frame(detector, sample) for sample in samples]

    total_frames = len(frame_results)
    frames_with_face = sum(1 for result in frame_results if result.faces)
    frames_with_multiple_faces = sum(1 for result in frame_results if len(result.faces) > 1)
    detection_rate = frames_with_face / total_frames if total_frames else 0

    primary_faces = [max(result.faces, key=lambda face: face.width * face.height) for result in frame_results if result.faces]
    center_jitter = _calculate_center_jitter(primary_faces)
    size_jitter = _calculate_size_jitter(primary_faces)

    risk_score = _calculate_face_risk_score(
        detection_rate=detection_rate,
        multiple_face_rate=frames_with_multiple_faces / total_frames if total_frames else 0,
        center_jitter=center_jitter,
        size_jitter=size_jitter,
    )

    return FaceConsistencyResult(
        total_frames_checked=total_frames,
        frames_with_face=frames_with_face,
        frames_with_multiple_faces=frames_with_multiple_faces,
        detection_rate=detection_rate,
        center_jitter=center_jitter,
        size_jitter=size_jitter,
        risk_score=risk_score,
        risk_level=_risk_level(risk_score, detection_rate),
        reasons=_build_reasons(
            detection_rate=detection_rate,
            frames_with_multiple_faces=frames_with_multiple_faces,
            center_jitter=center_jitter,
            size_jitter=size_jitter,
        ),
        frame_results=frame_results,
    )


def _load_face_detector() -> cv2.CascadeClassifier:
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))

    if detector.empty():
        raise ValueError("OpenCV face detector could not be loaded.")

    return detector


def _analyze_frame(detector: cv2.CascadeClassifier, sample: FrameSample) -> FaceFrameResult:
    image_rgb = sample.image_rgb
    image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    detected_faces = detector.detectMultiScale(
        image_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40),
    )

    faces = [FaceBox(int(x), int(y), int(width), int(height)) for x, y, width, height in detected_faces]
    annotated = image_rgb.copy()

    for face in faces:
        color = (255, 80, 80) if len(faces) > 1 else (0, 180, 90)
        top_left = (face.x, face.y)
        bottom_right = (face.x + face.width, face.y + face.height)
        cv2.rectangle(annotated, top_left, bottom_right, color, 3)

    return FaceFrameResult(
        frame_index=sample.frame_index,
        timestamp_seconds=sample.timestamp_seconds,
        faces=faces,
        annotated_image_rgb=annotated,
    )


def _calculate_center_jitter(faces: list[FaceBox]) -> float:
    if len(faces) < 2:
        return 0

    centers = np.array([(face.x + face.width / 2, face.y + face.height / 2) for face in faces])
    center_spread = np.std(centers, axis=0).mean()
    average_face_size = np.mean([(face.width + face.height) / 2 for face in faces])

    if average_face_size <= 0:
        return 0

    return float(center_spread / average_face_size)


def _calculate_size_jitter(faces: list[FaceBox]) -> float:
    if len(faces) < 2:
        return 0

    areas = np.array([face.width * face.height for face in faces])
    average_area = areas.mean()

    if average_area <= 0:
        return 0

    return float(areas.std() / average_area)


def _calculate_face_risk_score(
    detection_rate: float,
    multiple_face_rate: float,
    center_jitter: float,
    size_jitter: float,
) -> int:
    missing_face_risk = (1 - detection_rate) * 60
    multiple_face_risk = multiple_face_rate * 20
    center_risk = min(center_jitter * 45, 15)
    size_risk = min(size_jitter * 35, 15)

    return round(min(100, missing_face_risk + multiple_face_risk + center_risk + size_risk))


def _risk_level(risk_score: int, detection_rate: float) -> str:
    if detection_rate == 0:
        return "High"
    if risk_score >= 70:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"


def _build_reasons(
    detection_rate: float,
    frames_with_multiple_faces: int,
    center_jitter: float,
    size_jitter: float,
) -> list[str]:
    reasons = []

    if detection_rate == 0:
        reasons.append("No face detected in sampled frames")
    elif detection_rate < 0.6:
        reasons.append("Face missing in several sampled frames")
    else:
        reasons.append("Face detected consistently in sampled frames")

    if frames_with_multiple_faces:
        reasons.append("Multiple faces detected in one or more frames")

    if center_jitter > 0.35:
        reasons.append("Face position changes sharply across frames")

    if size_jitter > 0.35:
        reasons.append("Face size changes sharply across frames")

    if len(reasons) == 1 and detection_rate >= 0.6:
        reasons.append("No major face consistency warning in this scan")

    return reasons

