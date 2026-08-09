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


def build_rq1_posting_monthly_global_mart(postings: pd.DataFrame) -> pd.DataFrame:
    """RQ1 main grain: month; denominator: distinct canonical eligible postings."""
    required = {
        "postingId",
        "canonicalPostingId",
        "canonicalRecordFlag",
        "postingEligibleFlag",
        "periodMonth",
        "trackType",
    }
    missing = required.difference(postings.columns)
    if missing:
        raise ValueError(f"RQ1 global input missing: {sorted(missing)}")
    eligible = postings.loc[
        postings["postingEligibleFlag"].fillna(False)
        & postings["canonicalRecordFlag"].fillna(False)
    ].copy()
    rows = []
    for month, group in eligible.groupby("periodMonth", dropna=False):
        denominator = int(group["canonicalPostingId"].nunique())
        counts = group.groupby("trackType")["canonicalPostingId"].nunique().to_dict()
        rows.append(
            {
                "month": month,
                "canonicalEligiblePostingCount": denominator,
                "entryPostingCount": int(counts.get("entry", 0)),
                "internPostingCount": int(counts.get("intern", 0)),
                "experiencedPostingCount": int(counts.get("experienced", 0)),
                "denominatorDefinition": "distinct canonical eligible posting",
            }
        )
    return pd.DataFrame(rows)


def build_rq1_track_monthly_job_mart(tracks: pd.DataFrame) -> pd.DataFrame:
    """RQ1 job view grain: month x jobFamily x trackType; never labels tracks as postings."""
    required = {"trackId", "periodMonth", "jobFamily", "trackType", "rq1EligibleFlag"}
    missing = required.difference(tracks.columns)
    if missing:
        raise ValueError(f"RQ1 track input missing: {sorted(missing)}")
    eligible = tracks.loc[tracks["rq1EligibleFlag"].fillna(False)]
    return (
        eligible.groupby(["periodMonth", "jobFamily", "trackType"], dropna=False)["trackId"]
        .nunique()
        .rename("distinctTrackCount")
        .reset_index()
    )


def build_primary_job_share_mart(postings: pd.DataFrame) -> pd.DataFrame:
    required = {"periodMonth", "canonicalPostingId", "primaryJobStatus"}
    missing = required.difference(postings.columns)
    if missing:
        raise ValueError(f"primary-job input missing: {sorted(missing)}")
    rows = []
    for month, group in postings.groupby("periodMonth", dropna=False):
        status_by_posting = group.groupby("canonicalPostingId")["primaryJobStatus"].first()
        denominator = len(status_by_posting)

        shares = {
            value: float((status_by_posting == value).sum() / denominator) if denominator else None
            for value in ("resolved", "multi", "unknown")
        }
        rows.append(
            {
                "month": month,
                "distinctCanonicalPostingCount": denominator,
                "resolvedPrimaryJobShare": shares["resolved"],
                "multiJobShare": shares["multi"],
                "unknownJobShare": shares["unknown"],
            }
        )
    return pd.DataFrame(rows)
