from __future__ import annotations

from typing import Any

import pandas as pd

DEGREE_ORDER = {"highSchool": 0, "associate": 1, "bachelor": 2, "master": 3, "doctorate": 4}


def _truth(group: pd.DataFrame, column: str) -> bool:
    return bool(group[column].fillna(False).astype(bool).any()) if column in group else False


def _values(group: pd.DataFrame, column: str) -> list[str]:
    if column not in group:
        return []
    return sorted({str(value) for value in group[column].dropna() if str(value).strip()})


def _highest_degree(values: list[str]) -> str | None:
    if not values:
        return None
    return max(values, key=lambda value: DEGREE_ORDER.get(value, -1))


def aggregate_requirement_facts(
    tracks: pd.DataFrame,
    sections: pd.DataFrame,
    requirements: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate atomic facts without replacing observed evidence with constants."""
    required_track = {"trackId"}
    required_section = {"sectionId", "trackId"}
    required_fact = {"sectionId", "requirementType", "mandatoryFlag"}
    for frame, required, name in (
        (tracks, required_track, "tracks"),
        (sections, required_section, "sections"),
        (requirements, required_fact, "requirements"),
    ):
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")
    joined = requirements.merge(
        sections[["sectionId", "trackId"]], on="sectionId", how="left", validate="many_to_one"
    )
    if joined["trackId"].isna().any():
        raise ValueError("REQUIREMENT_SECTION_FK_VIOLATION")
    rows: list[dict[str, Any]] = []
    for track_id in tracks["trackId"].astype(str):
        group = joined.loc[joined["trackId"].astype(str) == track_id]
        mandatory = group.loc[group["mandatoryFlag"].fillna(False)]
        months = pd.to_numeric(mandatory.get("minCareerMonths"), errors="coerce").dropna()
        certificate_names = _values(mandatory, "rawCertificateName")
        certificate_classes = _values(mandatory, "nationalCertificateClass")
        degree_levels = _values(mandatory, "requiredDegreeLevel")
        tool_rows = (
            mandatory.loc[mandatory["requirementType"].isin(["tool", "skill"])]
            if not mandatory.empty
            else mandatory
        )
        rows.append(
            {
                "trackId": track_id,
                "minCareerMonths": int(months.max()) if not months.empty else None,
                "requiredExperienceFlag": bool(not months.empty),
                "requiredPriorExperienceFlag": _truth(mandatory, "priorExperienceFlag"),
                "requiredPortfolioFlag": _truth(mandatory, "portfolioFlag"),
                "requiredProjectFlag": _truth(mandatory, "projectFlag"),
                "requiredCertificateFlag": _truth(mandatory, "certificateFlag")
                or bool(certificate_names),
                "certificateClass": certificate_classes[0]
                if len(certificate_classes) == 1
                else None,
                "requiredDegreeLevel": _highest_degree(degree_levels),
                "requiredToolCount": int(len(tool_rows)),
                "requiredSkillCount": int(len(tool_rows)),
                "toolSpecificityCount": int(len(_values(tool_rows, "normalizedTextValue"))),
                "requirementFactCount": int(len(group)),
            }
        )
    return pd.DataFrame(rows)
