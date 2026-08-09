from __future__ import annotations

import pandas as pd

from p4.processing.requirements import aggregate_requirement_facts


def test_requirement_aggregation_preserves_degree_and_certificate() -> None:
    tracks = pd.DataFrame({"trackId": ["T1"]})
    sections = pd.DataFrame({"sectionId": ["S1"], "trackId": ["T1"]})
    requirements = pd.DataFrame(
        {
            "sectionId": ["S1", "S1", "S1"],
            "requirementType": ["degree", "certificate", "project"],
            "mandatoryFlag": [True, True, True],
            "degreeFlag": [True, False, False],
            "certificateFlag": [False, True, False],
            "projectFlag": [False, False, True],
            "requiredDegreeLevel": ["bachelor", None, None],
            "rawCertificateName": [None, "정보처리기사", None],
            "nationalCertificateClass": [None, "기사", None],
            "minCareerMonths": [None, None, None],
            "priorExperienceFlag": [False, False, False],
            "portfolioFlag": [False, False, False],
            "normalizedTextValue": ["학사", "정보처리기사", "프로젝트"],
        }
    )
    row = aggregate_requirement_facts(tracks, sections, requirements).iloc[0]
    assert row.requiredDegreeLevel == "bachelor"
    assert bool(row.requiredCertificateFlag) is True
    assert row.certificateClass == "기사"
    assert bool(row.requiredProjectFlag) is True
