from __future__ import annotations

import pandas as pd

from p4.processing.eligibility import recompute_fail_closed_eligibility


def test_unresolved_source_cannot_inherit_true_eligibility() -> None:
    postings = pd.DataFrame(
        {
            "postingId": ["P1", "P2"],
            "canonicalPostedAt": ["2026-01-01", None],
            "companyKey": ["C1", None],
            "activityTextAvailableFlag": [True, True],
            "externalDetailOnlyFlag": [False, False],
        }
    )
    tracks = pd.DataFrame(
        {
            "trackId": ["T1", "T2"],
            "postingId": ["P1", "P2"],
            "trackType": ["entry", "entry"],
            "mixedResolvedFlag": [True, True],
        }
    )
    sections = pd.DataFrame(
        {
            "trackId": ["T1", "T1", "T2", "T2"],
            "sectionType": ["required", "duty", "required", "duty"],
            "boundaryResolvedFlag": [True, True, True, True],
        }
    )
    result = recompute_fail_closed_eligibility(postings, tracks, sections).set_index("trackId")
    assert bool(result.loc["T1", "rq2EligibleFlag"]) is True
    assert bool(result.loc["T2", "postingEligibleFlag"]) is False
    assert "SOURCE_AUTHORITY_UNRESOLVED" in result.loc["T2", "eligibilityReasons"]
