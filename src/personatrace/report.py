from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RiskReport:
    risk_score: int
    risk_level: str
    reasons: list[str]
    planned_modules: list[str]


def build_placeholder_report(video_path: Path | None) -> RiskReport:
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

    return RiskReport(
        risk_score=35,
        risk_level="Initial Scan Pending",
        reasons=[
            "Video accepted for analysis",
            "Frame extraction will be added on Day 2",
            "Risk score is currently a placeholder",
        ],
        planned_modules=planned_modules,
    )

