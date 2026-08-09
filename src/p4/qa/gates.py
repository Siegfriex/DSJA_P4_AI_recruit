from __future__ import annotations

from pathlib import Path

BOOTSTRAP_GATES = (
    "REPOSITORY_BOOTSTRAP_READY",
    "DESIGN_SPEC_READY",
    "CONTRACT_BRIDGE_READY",
    "ENVIRONMENT_TEMPLATE_READY",
    "DATA_INVENTORY_EMPTY",
    "SOURCE_DATA_READY",
    "COLLECTION_IMPLEMENTATION_READY",
    "NCS_REFERENCE_READY",
    "ANALYSIS_READY",
)


def bootstrap_gate_table(*, root: Path, contract: dict, data: dict) -> list[dict]:
    design_docs = (
        root / "docs/01_SYSTEM_DESIGN_SPEC.md",
        root / "docs/02_DETAILED_DESIGN.md",
        root / "docs/03_IMPLEMENTATION_RUNBOOK.md",
    )
    environment_examples = tuple((root / "env").glob("*.env.example"))
    empty = data.get("status") == "EMPTY_BOOTSTRAP"
    return [
        {"gate": "REPOSITORY_BOOTSTRAP_READY", "status": "PASS"},
        {
            "gate": "DESIGN_SPEC_READY",
            "status": "PASS" if all(path.is_file() for path in design_docs) else "BLOCKED",
        },
        {"gate": "CONTRACT_BRIDGE_READY", "status": contract["status"]},
        {
            "gate": "ENVIRONMENT_TEMPLATE_READY",
            "status": "PASS" if len(environment_examples) >= 4 else "BLOCKED",
        },
        {"gate": "DATA_INVENTORY_EMPTY", "status": "PASS" if empty else "BLOCKED"},
        {"gate": "SOURCE_DATA_READY", "status": "BLOCKED" if empty else "NOT_EVALUATED"},
        {"gate": "COLLECTION_IMPLEMENTATION_READY", "status": "BLOCKED"},
        {"gate": "NCS_REFERENCE_READY", "status": "BLOCKED"},
        {"gate": "ANALYSIS_READY", "status": "BLOCKED"},
    ]
