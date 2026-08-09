from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LabelEvidence:
    track_type: str
    min_career_months: int | None
    prior_experience_required: bool
    boundary_resolved: bool


def career_class(evidence: LabelEvidence) -> str:
    if not evidence.boundary_resolved or evidence.track_type == "intern":
        return "U"
    months = evidence.min_career_months
    if evidence.track_type == "entry":
        return "E1" if evidence.prior_experience_required or (months or 0) > 0 else "E0"
    if evidence.track_type == "experienced" or (months or 0) >= 36:
        return "E3"
    if months is not None and 12 <= months <= 35:
        return "E2"
    return "U"


def intern_access_class(evidence: LabelEvidence) -> str | None:
    if evidence.track_type != "intern":
        return None
    if not evidence.boundary_resolved:
        return "IU"
    return (
        "I1"
        if evidence.prior_experience_required or (evidence.min_career_months or 0) > 0
        else "I0"
    )
