from __future__ import annotations

import pandas as pd


def semantic_summary(frames: dict[str, pd.DataFrame]) -> dict:
    posting = frames["posting_normalized"]
    preprocessed = frames["preprocessed_posting_tracks"]
    requirements = frames["requirement_facts"]
    labels = frames["career_access_labels"]
    valid_kinds = {"recruitUnknown", "recruitNewGrad", "recruitIntern", "recruitExperienced"}
    invalid_kind = int((~posting["postingKind"].isin(valid_kinds)).sum())
    non_null_high_demand = int(preprocessed["highDemandScore"].notna().sum())
    forbidden_valid_flag = any("validPostingFlag" in frame.columns for frame in frames.values())
    return {
        "status": "PASS_WITH_FINDINGS"
        if invalid_kind == 0 and non_null_high_demand == 0 and not forbidden_valid_flag
        else "FAIL",
        "canonicalAuthorityRows": int(posting["canonicalPostedAt"].notna().sum()),
        "canonicalUnresolvedRows": int(posting["canonicalPostedAt"].isna().sum()),
        "invalidPostingKindRows": invalid_kind,
        "highDemandScoreNonNullRows": non_null_high_demand,
        "validPostingFlagPresent": forbidden_valid_flag,
        "degreeFactRows": int(requirements.get("degreeFlag", False).fillna(False).sum()),
        "certificateFactRows": int(requirements.get("certificateFlag", False).fillna(False).sum()),
        "resolvedCareerBoundaryRows": int(labels["boundaryResolvedFlag"].fillna(False).sum()),
        "rq1EligibleRows": int(preprocessed["rq1EligibleFlag"].fillna(False).sum()),
        "rq2EligibleRows": int(preprocessed["rq2EligibleFlag"].fillna(False).sum()),
        "ncsEligibleRows": int(preprocessed["ncsEligibleFlag"].fillna(False).sum()),
    }
