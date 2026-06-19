from dataclasses import dataclass
from pathlib import Path

from src.personatrace.behavior_analysis import BehaviorAnalysisResult
from src.personatrace.face_analysis import FaceConsistencyResult
from src.personatrace.lip_sync_analysis import LipSyncAnalysisResult
from src.personatrace.video_quality_analysis import VideoQualityResult


@dataclass(frozen=True)
class RiskReport:
    risk_score: int
    risk_level: str
    reasons: list[str]
    planned_modules: list[str]


def build_placeholder_report(
    video_path: Path | None,
    face_result: FaceConsistencyResult | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    lip_sync_result: LipSyncAnalysisResult | None = None,
    quality_result: VideoQualityResult | None = None,
) -> RiskReport:
    planned_modules = [
        "Face consistency tracking",
        "Lip-sync mismatch detection",
        "Blink and face movement analysis",
        "Video quality artifact checks",
        "Voice-video mismatch scoring",
    ]

    if video_path is None:
        return RiskReport(
            risk_score=0,
            risk_level="Waiting for video",
            reasons=["No interview video uploaded yet"],
            planned_modules=planned_modules,
        )

    if face_result is not None:
        behavior_reasons = behavior_result.reasons if behavior_result is not None else []
        behavior_score = behavior_result.risk_score if behavior_result is not None else face_result.risk_score
        lip_sync_reasons = lip_sync_result.reasons if lip_sync_result is not None else []
        lip_sync_available = lip_sync_result is not None and lip_sync_result.audio_available
        lip_sync_score = lip_sync_result.risk_score if lip_sync_available else 0
        quality_reasons = quality_result.reasons if quality_result is not None else []
        quality_score = quality_result.risk_score if quality_result is not None else 0

        if lip_sync_available:
            combined_score = round(
                (face_result.risk_score * 0.3)
                + (behavior_score * 0.25)
                + (lip_sync_score * 0.3)
                + (quality_score * 0.15)
            )
        else:
            combined_score = round(
                (face_result.risk_score * 0.45)
                + (behavior_score * 0.35)
                + (quality_score * 0.2)
            )

        return RiskReport(
            risk_score=combined_score,
            risk_level=_risk_level(combined_score),
            reasons=[
                "Frame extraction and metadata scan completed",
                "Face consistency scan completed",
                "Blink and frozen face behavior scan completed",
                "Speech and mouth timing scan completed",
                "Video quality artifact scan completed",
                *face_result.reasons,
                *behavior_reasons,
                *lip_sync_reasons,
                *quality_reasons,
            ],
            planned_modules=planned_modules,
        )

    return RiskReport(
        risk_score=35,
        risk_level="Initial Scan Pending",
        reasons=[
            "Video accepted for analysis",
            "Frame extraction and metadata scan completed",
            "Risk score is still a placeholder until detection modules are added",
        ],
        planned_modules=planned_modules,
    )


def _risk_level(risk_score: int) -> str:
    if risk_score >= 70:
        return "High"
    if risk_score >= 40:
        return "Medium"
    return "Low"
