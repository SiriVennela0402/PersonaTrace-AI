from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.personatrace.face_analysis import FaceBox, FaceConsistencyResult


@dataclass(frozen=True)
class BehaviorAnalysisResult:
    frames_checked: int
    frames_with_face: int
    eye_signal_rate: float
    blink_event_count: int
    motion_variation: float
    risk_score: int
    risk_level: str
    reasons: list[str]


def analyze_behavior_patterns(face_result: FaceConsistencyResult) -> BehaviorAnalysisResult:
    frames_with_face = [frame for frame in face_result.frame_results if frame.faces]
    total_frames = len(face_result.frame_results)

    if not frames_with_face:
        return BehaviorAnalysisResult(
            frames_checked=total_frames,
            frames_with_face=0,
            eye_signal_rate=0,
            blink_event_count=0,
            motion_variation=0,
            risk_score=45,
            risk_level="Medium",
            reasons=["Behavior scan skipped because no face was detected"],
        )

    eye_detector = _load_eye_detector()
    eye_states: list[bool] = []
    face_crops: list[np.ndarray] = []

    for frame in frames_with_face:
        primary_face = max(frame.faces, key=lambda face: face.width * face.height)
        eye_states.append(_has_visible_eye_signal(eye_detector, frame.annotated_image_rgb, primary_face))
        face_crop = _extract_face_crop(frame.annotated_image_rgb, primary_face)
        if face_crop is not None:
            face_crops.append(face_crop)

    eye_signal_rate = sum(eye_states) / len(eye_states) if eye_states else 0
    blink_event_count = _count_blink_events(eye_states)
    motion_variation = _calculate_motion_variation(face_crops)
    risk_score = _calculate_behavior_risk(
        eye_signal_rate=eye_signal_rate,
        blink_event_count=blink_event_count,
        motion_variation=motion_variation,
        frames_with_face=len(frames_with_face),
    )

    return BehaviorAnalysisResult(
        frames_checked=total_frames,
        frames_with_face=len(frames_with_face),
        eye_signal_rate=eye_signal_rate,
        blink_event_count=blink_event_count,
        motion_variation=motion_variation,
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        reasons=_build_reasons(
            eye_signal_rate=eye_signal_rate,
            blink_event_count=blink_event_count,
            motion_variation=motion_variation,
            frames_with_face=len(frames_with_face),
        ),
    )


def _load_eye_detector() -> cv2.CascadeClassifier:
    cascade_names = ["haarcascade_eye_tree_eyeglasses.xml", "haarcascade_eye.xml"]
    for cascade_name in cascade_names:
        cascade_path = Path(cv2.data.haarcascades) / cascade_name
        detector = cv2.CascadeClassifier(str(cascade_path))
        if not detector.empty():
            return detector

    raise ValueError("OpenCV eye detector could not be loaded.")


def _has_visible_eye_signal(
    detector: cv2.CascadeClassifier,
    image_rgb: np.ndarray,
    face: FaceBox,
) -> bool:
    x1 = max(face.x, 0)
    y1 = max(face.y, 0)
    x2 = min(face.x + face.width, image_rgb.shape[1])
    y2 = min(face.y + int(face.height * 0.62), image_rgb.shape[0])

    if x2 <= x1 or y2 <= y1:
        return False

    upper_face = image_rgb[y1:y2, x1:x2]
    gray = cv2.cvtColor(upper_face, cv2.COLOR_RGB2GRAY)
    eyes = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(12, 12),
    )

    return len(eyes) > 0


def _extract_face_crop(image_rgb: np.ndarray, face: FaceBox) -> np.ndarray | None:
    x1 = max(face.x, 0)
    y1 = max(face.y, 0)
    x2 = min(face.x + face.width, image_rgb.shape[1])
    y2 = min(face.y + face.height, image_rgb.shape[0])

    if x2 <= x1 or y2 <= y1:
        return None

    crop = image_rgb[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    return cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)


def _count_blink_events(eye_states: list[bool]) -> int:
    if len(eye_states) < 3:
        return 0

    blink_count = 0
    for previous_state, current_state, next_state in zip(eye_states, eye_states[1:], eye_states[2:]):
        if previous_state and not current_state and next_state:
            blink_count += 1

    return blink_count


def _calculate_motion_variation(face_crops: list[np.ndarray]) -> float:
    if len(face_crops) < 2:
        return 0

    differences = []
    for previous_crop, current_crop in zip(face_crops, face_crops[1:]):
        diff = cv2.absdiff(previous_crop, current_crop)
        differences.append(float(diff.mean() / 255))

    return float(np.mean(differences)) if differences else 0


def _calculate_behavior_risk(
    eye_signal_rate: float,
    blink_event_count: int,
    motion_variation: float,
    frames_with_face: int,
) -> int:
    weak_eye_risk = (1 - eye_signal_rate) * 35
    blink_risk = 25 if frames_with_face >= 6 and blink_event_count == 0 else 0
    frozen_risk = 30 if frames_with_face >= 4 and motion_variation < 0.015 else 0
    low_motion_risk = 10 if 0.015 <= motion_variation < 0.035 else 0

    return round(min(100, weak_eye_risk + blink_risk + frozen_risk + low_motion_risk))


def _risk_level(risk_score: int) -> str:
    if risk_score >= 70:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"


def _build_reasons(
    eye_signal_rate: float,
    blink_event_count: int,
    motion_variation: float,
    frames_with_face: int,
) -> list[str]:
    reasons = []

    if eye_signal_rate < 0.35:
        reasons.append("Weak eye visibility across face frames")
    else:
        reasons.append("Eye signal detected in the face region")

    if frames_with_face >= 6 and blink_event_count == 0:
        reasons.append("Low blink variation in sampled frames")
    elif blink_event_count > 0:
        reasons.append("Blink-like eye state change detected")

    if frames_with_face >= 4 and motion_variation < 0.015:
        reasons.append("Very low face motion suggests a frozen or static face")
    elif motion_variation < 0.035:
        reasons.append("Limited face motion variation")
    else:
        reasons.append("Face motion variation appears present")

    return reasons

