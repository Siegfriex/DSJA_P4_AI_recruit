from __future__ import annotations

import pandas as pd


def build_posting_mart(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "trackId",
        "canonicalPostingId",
        "periodMonth",
        "trackType",
        "rq1EligibleFlag",
        "empiricalAnalysisAllowed",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"posting mart input missing: {sorted(missing)}")
    if not frame["empiricalAnalysisAllowed"].fillna(False).all():
        raise ValueError("POSTING_MART_REQUIRES_EMPIRICAL_PROVENANCE")
    return frame.loc[frame["rq1EligibleFlag"]].copy()
