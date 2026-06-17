from dataclasses import dataclass
from pathlib import Path

from src.personatrace.face_analysis import FaceConsistencyResult


@dataclass(frozen=True)
class RiskReport:
    risk_score: int
    risk_level: str
    reasons: list[str]
    planned_modules: list[str]


def build_placeholder_report(
    video_path: Path | None,
    face_result: FaceConsistencyResult | None = None,
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
        return RiskReport(
            risk_score=face_result.risk_score,
            risk_level=face_result.risk_level,
            reasons=[
                "Frame extraction and metadata scan completed",
                "Face consistency scan completed",
                *face_result.reasons,
                "Lip-sync and blink analysis are not added yet",
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
