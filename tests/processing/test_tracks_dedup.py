from __future__ import annotations

import pandas as pd
import pytest

from p4.processing.dedup import assign_repost_groups
from p4.processing.tracks import validate_track_split


def test_unresolved_observed_track_is_marked_and_production_rejected() -> None:
    tracks = pd.DataFrame(
        {
            "trackId": ["T"],
            "postingId": ["P"],
            "trackType": ["mixedUnresolved"],
            "trackOrdinal": [0],
            "mixedResolvedFlag": [False],
        }
    )
    assert (
        validate_track_split(tracks, mode="observed").iloc[0].trackSplitStatus
        == "LEGACY_SINGLE_TRACK_OBSERVED"
    )
    with pytest.raises(ValueError, match="PRODUCTION_TRACK_SPLIT_UNRESOLVED"):
        validate_track_split(tracks, mode="production")


def test_90_day_repost_grouping() -> None:
    frame = pd.DataFrame(
        {
            "postingId": ["P1", "P2"],
            "companyKey": ["C", "C"],
            "titleText": ["AI Engineer", "AI Engineer"],
            "canonicalPostedAt": ["2026-01-01", "2026-02-01"],
            "postingEligibleFlag": [True, True],
        }
    )
    result = assign_repost_groups(frame)
    assert result.duplicateGroupId.nunique() == 1
    assert result.canonicalRecordFlag.tolist() == [True, False]
