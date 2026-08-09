from __future__ import annotations

import pandas as pd
import pytest

from p4.marts.posting import build_posting_mart


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
