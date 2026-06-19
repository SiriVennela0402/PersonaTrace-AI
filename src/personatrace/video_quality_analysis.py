from dataclasses import dataclass

import cv2
import numpy as np

from src.personatrace.video_analysis import VideoAnalysisResult


@dataclass(frozen=True)
class VideoQualityResult:
    frames_checked: int
    blur_score: float
    brightness_variation: float
    glitch_rate: float
    risk_score: int
    risk_level: str
    reasons: list[str]


def analyze_video_quality(analysis: VideoAnalysisResult) -> VideoQualityResult:
    frames = [sample.image_rgb for sample in analysis.sampled_frames]
    if not frames:
        return VideoQualityResult(
            frames_checked=0,
            blur_score=0,
            brightness_variation=0,
            glitch_rate=0,
            risk_score=35,
            risk_level="Medium",
            reasons=["Video quality scan skipped because no frames were extracted"],
        )

    blur_values = [_calculate_blur_value(frame) for frame in frames]
    brightness_values = [_calculate_brightness(frame) for frame in frames]
    frame_diffs = _calculate_frame_differences(frames)

    blur_score = float(np.mean(blur_values))
    brightness_variation = _safe_variation(brightness_values)
    glitch_rate = _calculate_glitch_rate(frame_diffs)
    risk_score = _calculate_quality_risk(blur_score, brightness_variation, glitch_rate)

    return VideoQualityResult(
        frames_checked=len(frames),
        blur_score=blur_score,
        brightness_variation=brightness_variation,
        glitch_rate=glitch_rate,
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        reasons=_build_reasons(blur_score, brightness_variation, glitch_rate),
    )


def _calculate_blur_value(image_rgb: np.ndarray) -> float:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _calculate_brightness(image_rgb: np.ndarray) -> float:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    return float(gray.mean())


def _calculate_frame_differences(frames: list[np.ndarray]) -> list[float]:
    if len(frames) < 2:
        return []

    differences = []
    previous_gray = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
    previous_gray = cv2.resize(previous_gray, (96, 54), interpolation=cv2.INTER_AREA)

    for frame in frames[1:]:
        current_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        current_gray = cv2.resize(current_gray, (96, 54), interpolation=cv2.INTER_AREA)
        diff = cv2.absdiff(previous_gray, current_gray)
        differences.append(float(diff.mean() / 255))
        previous_gray = current_gray

    return differences


def _safe_variation(values: list[float]) -> float:
    if len(values) < 2:
        return 0

    mean_value = float(np.mean(values))
    if mean_value <= 0:
        return 0

    return float(np.std(values) / mean_value)


def _calculate_glitch_rate(frame_diffs: list[float]) -> float:
    if not frame_diffs:
        return 0

    median_diff = float(np.median(frame_diffs))
    std_diff = float(np.std(frame_diffs))
    threshold = max(0.38, median_diff + (std_diff * 2.6))
    glitches = sum(1 for diff in frame_diffs if diff > threshold)
    return glitches / len(frame_diffs)


def _calculate_quality_risk(
    blur_score: float,
    brightness_variation: float,
    glitch_rate: float,
) -> int:
    blur_risk = 35 if blur_score < 45 else 20 if blur_score < 90 else 0
    lighting_risk = min(brightness_variation * 95, 30)
    glitch_risk = min(glitch_rate * 80, 35)
    return round(min(100, blur_risk + lighting_risk + glitch_risk))


def _risk_level(risk_score: int) -> str:
    if risk_score >= 70:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"


def _build_reasons(
    blur_score: float,
    brightness_variation: float,
    glitch_rate: float,
) -> list[str]:
    reasons = []

    if blur_score < 45:
        reasons.append("Very low sharpness detected in sampled frames")
    elif blur_score < 90:
        reasons.append("Moderate blur detected in sampled frames")
    else:
        reasons.append("Frame sharpness appears acceptable")

    if brightness_variation > 0.28:
        reasons.append("Lighting changes sharply across sampled frames")
    elif brightness_variation > 0.16:
        reasons.append("Moderate lighting variation detected")
    else:
        reasons.append("Lighting variation appears stable")

    if glitch_rate > 0.25:
        reasons.append("Possible frame glitch or abrupt visual jump detected")
    elif glitch_rate > 0:
        reasons.append("Minor abrupt frame change detected")
    else:
        reasons.append("No major frame glitch detected in sampled frames")

    return reasons

