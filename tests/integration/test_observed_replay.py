from __future__ import annotations

from pathlib import Path

import pytest

from p4.processing.replay import replay_observed

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/staging/legacy_observed/M1_5_RECONCILIATION_20260807_06"


@pytest.mark.skipif(not SOURCE.exists(), reason="local-only observed bundle is not present in CI")
def test_local_observed_replay_closes_known_semantic_export_defects(tmp_path: Path) -> None:
    report = replay_observed(SOURCE, tmp_path / "replay")
    assert report["counts"]["posting_normalized"]["new"] == 137
    assert report["counts"]["source_blocks"]["new"] == 84
    assert report["counts"]["semantic_chunks"]["new"] == 277
    assert report["counts"]["requirement_facts"]["new"] == 41
    assert report["intentionalFeatureDeltas"]["requiredCertificateFlagTrue"] == 2
    assert report["intentionalFeatureDeltas"]["requiredDegreeLevelPresent"] == 10
    assert report["intentionalFeatureDeltas"]["postingEligibleNew"] == 29
    assert report["intentionalFeatureDeltas"]["rq2EligibleNew"] == 10
    assert report["networkCalls"] == 0
