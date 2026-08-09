from __future__ import annotations

import pandas as pd


def build_time_series(posting_mart: pd.DataFrame) -> pd.DataFrame:
    required = {"canonicalPostingId", "periodMonth", "trackType"}
    missing = required.difference(posting_mart.columns)
    if missing:
        raise ValueError(f"time-series input missing: {sorted(missing)}")
    rows = []
    for month, group in posting_mart.groupby("periodMonth", dropna=False):
        denominator = int(group["canonicalPostingId"].nunique())
        counts = group.groupby("trackType")["canonicalPostingId"].nunique().to_dict()
        rows.append(
            {
                "periodMonth": month,
                "denominator": denominator,
                "entryPostingRate": counts.get("entry", 0) / denominator if denominator else None,
                "internPostingRate": counts.get("intern", 0) / denominator if denominator else None,
                "experiencedOnlyRate": counts.get("experienced", 0) / denominator
                if denominator
                else None,
            }
        )
    return pd.DataFrame(rows)
