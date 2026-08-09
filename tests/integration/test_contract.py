from __future__ import annotations

from pathlib import Path

from p4.qa.schema import validate_contract

ROOT = Path(__file__).resolve().parents[2]


def test_contract_bridge_preserves_legacy_and_adds_only_executed_entities() -> None:
    report = validate_contract(ROOT)
    assert report["legacyTableCount"] == 26
    assert report["bridgeTableCount"] == 29
    assert report["addedTables"] == [
        "core.postingSourceBlock",
        "core.sectionSourceBlock",
        "core.semanticChunk",
    ]
