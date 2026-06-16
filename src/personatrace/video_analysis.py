from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class VideoMetadata:
    filename: str
    frame_count: int
    fps: float
    duration_seconds: float
    width: int
    height: int


@dataclass(frozen=True)
class FrameSample:
    frame_index: int
    timestamp_seconds: float
    image_rgb: np.ndarray


@dataclass(frozen=True)
class VideoAnalysisResult:
    metadata: VideoMetadata
    sampled_frames: list[FrameSample]


def analyze_video(video_path: Path, sample_count: int = 6) -> VideoAnalysisResult:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("Could not open the uploaded video file.")

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_seconds = frame_count / fps if fps > 0 else 0

    metadata = VideoMetadata(
        filename=video_path.name,
        frame_count=frame_count,
        fps=fps,
        duration_seconds=duration_seconds,
        width=width,
        height=height,
    )

    sampled_frames = _sample_frames(capture, frame_count, fps, sample_count)
    capture.release()

    return VideoAnalysisResult(metadata=metadata, sampled_frames=sampled_frames)


def _sample_frames(
    capture: cv2.VideoCapture,
    frame_count: int,
    fps: float,
    sample_count: int,
) -> list[FrameSample]:
    if frame_count <= 0:
        return []

    safe_sample_count = max(1, min(sample_count, frame_count))
    frame_indices = np.linspace(0, frame_count - 1, safe_sample_count, dtype=int)
    samples: list[FrameSample] = []

    for frame_index in frame_indices:
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
        success, frame_bgr = capture.read()

        if not success:
            continue

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        timestamp_seconds = frame_index / fps if fps > 0 else 0
        samples.append(
            FrameSample(
                frame_index=int(frame_index),
                timestamp_seconds=float(timestamp_seconds),
                image_rgb=frame_rgb,
            )
        )

    return samples

