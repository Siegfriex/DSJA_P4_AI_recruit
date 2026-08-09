from __future__ import annotations

import pandas as pd

RESOLVED_TRACK_TYPES = {"entry", "intern", "experienced", "mixedResolved"}


def recompute_fail_closed_eligibility(
    postings: pd.DataFrame,
    tracks: pd.DataFrame,
    sections: pd.DataFrame,
) -> pd.DataFrame:
    """Recompute eligibility from current authority instead of inherited booleans.

    Observed rows without authoritative date and company remain present for
    diagnostics but cannot enter production denominators.
    """
    posting_required = {
        "postingId",
        "canonicalPostedAt",
        "companyKey",
        "activityTextAvailableFlag",
        "externalDetailOnlyFlag",
    }
    track_required = {"trackId", "postingId", "trackType", "mixedResolvedFlag"}
    section_required = {"trackId", "sectionType", "boundaryResolvedFlag"}
    for frame, required, name in (
        (postings, posting_required, "postings"),
        (tracks, track_required, "tracks"),
        (sections, section_required, "sections"),
    ):
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{name} missing eligibility columns: {sorted(missing)}")
    resolved_boundary = set(
        sections.loc[
            sections["sectionType"].isin(["required", "preferred"])
            & sections["boundaryResolvedFlag"].fillna(False),
            "trackId",
        ].astype(str)
    )
    duty_available = set(
        sections.loc[
            sections["sectionType"].eq("duty") & sections["boundaryResolvedFlag"].fillna(False),
            "trackId",
        ].astype(str)
    )
    merged = tracks.merge(
        postings[
            [
                "postingId",
                "canonicalPostedAt",
                "companyKey",
                "activityTextAvailableFlag",
                "externalDetailOnlyFlag",
            ]
        ],
        on="postingId",
        how="left",
        validate="many_to_one",
    )
    rows = []
    for row in merged.to_dict(orient="records"):
        track_id = str(row["trackId"])
        source_authority = pd.notna(row["canonicalPostedAt"]) and pd.notna(row["companyKey"])
        track_resolved = bool(row["mixedResolvedFlag"]) and row["trackType"] in RESOLVED_TRACK_TYPES
        boundary = track_id in resolved_boundary
        body = bool(row["activityTextAvailableFlag"]) and not bool(row["externalDetailOnlyFlag"])
        posting_eligible = bool(source_authority)
        rq1 = posting_eligible and track_resolved
        rq2 = posting_eligible and track_resolved and boundary and body
        ncs = posting_eligible and track_resolved and track_id in duty_available and body
        reasons = []
        if not source_authority:
            reasons.append("SOURCE_AUTHORITY_UNRESOLVED")
        if not track_resolved:
            reasons.append("TRACK_UNRESOLVED")
        if not boundary:
            reasons.append("REQUIRED_PREFERRED_BOUNDARY_UNRESOLVED")
        if not body:
            reasons.append("USABLE_BODY_UNAVAILABLE")
        rows.append(
            {
                "trackId": track_id,
                "postingEligibleFlag": posting_eligible,
                "rq1EligibleFlag": rq1,
                "rq2EligibleFlag": rq2,
                "ncsEligibleFlag": ncs,
                "eligibilityStatus": "RESOLVED" if not reasons else "FAIL_CLOSED",
                "eligibilityReasons": reasons,
                "eligibilityVersion": "p4-eligibility-2.1.3",
            }
        )
    return pd.DataFrame(rows)
