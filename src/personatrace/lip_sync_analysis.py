from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess
import wave

import cv2
import imageio_ffmpeg
import numpy as np

from src.personatrace.face_analysis import FaceBox, FaceConsistencyResult


@dataclass(frozen=True)
class LipSyncAnalysisResult:
    audio_available: bool
    frames_checked: int
    speech_activity_rate: float
    mouth_activity_rate: float
    mismatch_rate: float
    risk_score: int
    risk_level: str
    reasons: list[str]


def analyze_lip_sync(video_path: Path, face_result: FaceConsistencyResult) -> LipSyncAnalysisResult:
    frames_with_face = [frame for frame in face_result.frame_results if frame.faces]
    if not frames_with_face:
        return LipSyncAnalysisResult(
            audio_available=False,
            frames_checked=len(face_result.frame_results),
            speech_activity_rate=0,
            mouth_activity_rate=0,
            mismatch_rate=0,
            risk_score=0,
            risk_level="Unavailable",
            reasons=["Lip-sync scan skipped because no face was detected"],
        )

    audio_samples, sample_rate = _extract_audio_samples(video_path)
    if audio_samples is None or sample_rate == 0:
        return LipSyncAnalysisResult(
            audio_available=False,
            frames_checked=len(frames_with_face),
            speech_activity_rate=0,
            mouth_activity_rate=_estimate_mouth_activity_rate(frames_with_face),
            mismatch_rate=0,
            risk_score=0,
            risk_level="Unavailable",
            reasons=["Audio track unavailable, so speech-mouth timing could not be checked"],
        )

    timestamps = [frame.timestamp_seconds for frame in frames_with_face]
    speech_states = _speech_states_for_timestamps(audio_samples, sample_rate, timestamps)
    mouth_states = _mouth_states_for_frames(frames_with_face)
    aligned_length = min(len(speech_states), len(mouth_states))

    if aligned_length == 0:
        return LipSyncAnalysisResult(
            audio_available=True,
            frames_checked=0,
            speech_activity_rate=0,
            mouth_activity_rate=0,
            mismatch_rate=0,
            risk_score=0,
            risk_level="Unavailable",
            reasons=["Not enough aligned audio-video samples for lip-sync scoring"],
        )

    speech_states = speech_states[:aligned_length]
    mouth_states = mouth_states[:aligned_length]
    speech_activity_rate = sum(speech_states) / aligned_length
    mouth_activity_rate = sum(mouth_states) / aligned_length
    mismatches = sum(1 for speech, mouth in zip(speech_states, mouth_states) if speech and not mouth)
    mismatch_rate = mismatches / aligned_length
    risk_score = _calculate_lip_sync_risk(speech_activity_rate, mouth_activity_rate, mismatch_rate)

    return LipSyncAnalysisResult(
        audio_available=True,
        frames_checked=aligned_length,
        speech_activity_rate=speech_activity_rate,
        mouth_activity_rate=mouth_activity_rate,
        mismatch_rate=mismatch_rate,
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        reasons=_build_reasons(speech_activity_rate, mouth_activity_rate, mismatch_rate),
    )


def _extract_audio_samples(video_path: Path) -> tuple[np.ndarray | None, int]:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_path = Path(temp_audio.name)

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        str(audio_path),
    ]

    try:
        completed = subprocess.run(command, capture_output=True, check=False)
        if completed.returncode != 0 or not audio_path.exists() or audio_path.stat().st_size == 0:
            return None, 0

        with wave.open(str(audio_path), "rb") as audio_file:
            sample_rate = audio_file.getframerate()
            raw_frames = audio_file.readframes(audio_file.getnframes())

        samples = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32) / 32768.0
        return samples, sample_rate
    finally:
        try:
            audio_path.unlink(missing_ok=True)
        except OSError:
            pass


def _speech_states_for_timestamps(
    audio_samples: np.ndarray,
    sample_rate: int,
    timestamps: list[float],
) -> list[bool]:
    if len(audio_samples) == 0:
        return [False for _ in timestamps]

    energies = []
    half_window = int(sample_rate * 0.18)
    for timestamp in timestamps:
        center = int(timestamp * sample_rate)
        start = max(0, center - half_window)
        end = min(len(audio_samples), center + half_window)
        window = audio_samples[start:end]
        energy = float(np.sqrt(np.mean(np.square(window)))) if len(window) else 0
        energies.append(energy)

    if not energies:
        return []

    threshold = max(0.018, float(np.median(energies) + np.std(energies) * 0.45))
    return [energy > threshold for energy in energies]


def _mouth_states_for_frames(frames_with_face) -> list[bool]:
    movements = _mouth_movement_values(frames_with_face)
    if not movements:
        return []

    threshold = max(0.012, float(np.median(movements) + np.std(movements) * 0.35))
    return [movement > threshold for movement in movements]


def _estimate_mouth_activity_rate(frames_with_face) -> float:
    mouth_states = _mouth_states_for_frames(frames_with_face)
    if not mouth_states:
        return 0
    return sum(mouth_states) / len(mouth_states)


def _mouth_movement_values(frames_with_face) -> list[float]:
    mouth_crops = []
    for frame in frames_with_face:
        primary_face = max(frame.faces, key=lambda face: face.width * face.height)
        crop = _extract_mouth_crop(frame.annotated_image_rgb, primary_face)
        if crop is not None:
            mouth_crops.append(crop)

    if len(mouth_crops) < 2:
        return []

    movements = []
    for previous_crop, current_crop in zip(mouth_crops, mouth_crops[1:]):
        diff = cv2.absdiff(previous_crop, current_crop)
        movements.append(float(diff.mean() / 255))

    if movements:
        movements.insert(0, movements[0])

    return movements


def _extract_mouth_crop(image_rgb: np.ndarray, face: FaceBox) -> np.ndarray | None:
    x1 = max(face.x + int(face.width * 0.18), 0)
    y1 = max(face.y + int(face.height * 0.58), 0)
    x2 = min(face.x + int(face.width * 0.82), image_rgb.shape[1])
    y2 = min(face.y + int(face.height * 0.92), image_rgb.shape[0])

    if x2 <= x1 or y2 <= y1:
        return None

    crop = image_rgb[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    return cv2.resize(gray, (64, 32), interpolation=cv2.INTER_AREA)


def _calculate_lip_sync_risk(
    speech_activity_rate: float,
    mouth_activity_rate: float,
    mismatch_rate: float,
) -> int:
    speech_without_mouth_risk = mismatch_rate * 65
    weak_mouth_risk = 25 if speech_activity_rate > 0.25 and mouth_activity_rate < 0.12 else 0
    low_signal_risk = 10 if speech_activity_rate > 0.35 and mouth_activity_rate < 0.25 else 0
    return round(min(100, speech_without_mouth_risk + weak_mouth_risk + low_signal_risk))


def _risk_level(risk_score: int) -> str:
    if risk_score >= 70:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"


def _build_reasons(
    speech_activity_rate: float,
    mouth_activity_rate: float,
    mismatch_rate: float,
) -> list[str]:
    reasons = []

    if speech_activity_rate < 0.12:
        reasons.append("Low speech activity detected in the audio track")
    else:
        reasons.append("Speech activity detected in the audio track")

    if mouth_activity_rate < 0.12:
        reasons.append("Weak mouth-region movement across face frames")
    else:
        reasons.append("Mouth-region movement detected")

    if mismatch_rate > 0.45:
        reasons.append("Speech activity appears without matching mouth movement")
    elif mismatch_rate > 0.2:
        reasons.append("Possible speech-mouth timing mismatch")
    else:
        reasons.append("No strong lip-sync mismatch in sampled windows")

    return reasons

