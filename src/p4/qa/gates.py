from __future__ import annotations

MIGRATION_GATES = (
    "NEW_REPO_BOOTSTRAPPED",
    "LEGACY_PROVENANCE_FROZEN",
    "CONTRACT_2_1_3_READY",
    "CORE_MODULES_MIGRATED",
    "OBSERVED_DATA_MIGRATED",
    "OBSERVED_REPLAY_READY",
    "STRUCTURAL_QA_READY",
    "SEMANTIC_REMEDIATION_READY",
    "CANARY_PREFLIGHT_READY",
)


def migration_gate_table(*, replay: dict | None, contract: dict, data: dict) -> list[dict]:
    replay_ready = replay is not None and replay.get("status") == "PASS_WITH_FINDINGS"
    data_ready = (
        data.get("raw", {}).get("status") == "PASS"
        and data.get("observed", {}).get("status") == "PASS"
    )
    return [
        {"gate": "NEW_REPO_BOOTSTRAPPED", "status": "PASS"},
        {"gate": "LEGACY_PROVENANCE_FROZEN", "status": "PASS"},
        {"gate": "CONTRACT_2_1_3_READY", "status": contract["status"]},
        {"gate": "CORE_MODULES_MIGRATED", "status": "PASS_WITH_FINDINGS"},
        {"gate": "OBSERVED_DATA_MIGRATED", "status": "PASS" if data_ready else "FAIL"},
        {
            "gate": "OBSERVED_REPLAY_READY",
            "status": "PASS_WITH_FINDINGS" if replay_ready else "BLOCKED",
        },
        {
            "gate": "STRUCTURAL_QA_READY",
            "status": "PASS" if replay_ready and data_ready else "BLOCKED",
        },
        {
            "gate": "SEMANTIC_REMEDIATION_READY",
            "status": "PASS_WITH_FINDINGS" if replay_ready else "BLOCKED",
        },
        {"gate": "CANARY_PREFLIGHT_READY", "status": "PARTIAL"},
    ]
