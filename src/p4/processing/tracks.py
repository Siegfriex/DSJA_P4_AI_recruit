from __future__ import annotations

import pandas as pd


def validate_track_split(tracks: pd.DataFrame, *, mode: str) -> pd.DataFrame:
    required = {"trackId", "postingId", "trackType", "trackOrdinal", "mixedResolvedFlag"}
    missing = required.difference(tracks.columns)
    if missing:
        raise ValueError(f"tracks missing columns: {sorted(missing)}")
    result = tracks.copy()
    result["trackSplitStatus"] = "LEGACY_SINGLE_TRACK_OBSERVED"
    if mode == "production":
        unresolved = ~result["mixedResolvedFlag"].fillna(False) | result["trackType"].isin(
            ["unknown", "mixedUnresolved"]
        )
        if unresolved.any():
            raise ValueError("PRODUCTION_TRACK_SPLIT_UNRESOLVED")
        result["trackSplitStatus"] = "RESOLVED"
    elif mode != "observed":
        raise ValueError("mode must be observed or production")
    return result
