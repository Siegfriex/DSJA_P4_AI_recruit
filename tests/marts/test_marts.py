from __future__ import annotations

import pandas as pd
import pytest

from p4.marts.posting import build_posting_mart
from p4.marts.timeseries import (
    build_primary_job_share_mart,
    build_rq1_posting_monthly_global_mart,
    build_rq1_track_monthly_job_mart,
)


def test_observed_data_cannot_build_empirical_mart() -> None:
    frame = pd.DataFrame(
        {
            "trackId": ["T"],
            "canonicalPostingId": ["P"],
            "periodMonth": ["2026-01"],
            "trackType": ["entry"],
            "rq1EligibleFlag": [True],
            "empiricalAnalysisAllowed": [False],
        }
    )
    with pytest.raises(ValueError, match="EMPIRICAL_PROVENANCE"):
        build_posting_mart(frame)


def test_rq1_grains_and_denominators_are_explicit() -> None:
    postings = pd.DataFrame(
        {
            "postingId": ["P1", "P2", "P3"],
            "canonicalPostingId": ["P1", "P1", "P3"],
            "canonicalRecordFlag": [True, False, True],
            "postingEligibleFlag": [True, True, True],
            "periodMonth": ["2026-01"] * 3,
            "trackType": ["entry", "entry", "intern"],
            "primaryJobStatus": ["resolved", "resolved", "multi"],
        }
    )
    global_mart = build_rq1_posting_monthly_global_mart(postings)
    assert global_mart.iloc[0].canonicalEligiblePostingCount == 2
    assert global_mart.iloc[0].denominatorDefinition == "distinct canonical eligible posting"
    shares = build_primary_job_share_mart(postings)
    assert shares.iloc[0].resolvedPrimaryJobShare == 0.5
    assert shares.iloc[0].multiJobShare == 0.5

    tracks = pd.DataFrame(
        {
            "trackId": ["T1", "T2"],
            "periodMonth": ["2026-01", "2026-01"],
            "jobFamily": ["data", "data"],
            "trackType": ["entry", "entry"],
            "rq1EligibleFlag": [True, True],
        }
    )
    track_mart = build_rq1_track_monthly_job_mart(tracks)
    assert track_mart.iloc[0].distinctTrackCount == 2
