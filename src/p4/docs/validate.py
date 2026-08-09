from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

import yaml

from p4.docs.hashing import sha256_path
from p4.docs.registry import source_release_integrity
from p4.docs.sync import GENERATED_PATHS, build_generated_documents

VALID_GATE_STATUS = {"PASS", "PASS_WITH_FINDINGS", "PARTIAL", "BLOCKED", "NOT_EVALUATED", "FAIL"}
LINK_PATTERN = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def _broken_links(root: Path) -> list[str]:
    failures = []
    for path in (root / "docs").rglob("*.md"):
        for target in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"{path.relative_to(root)} -> {target}")
    return failures


def _tracked_empirical(root: Path) -> list[str]:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines()
    forbidden_suffixes = (".duckdb", ".parquet", ".html.gz", ".onnx", ".npy", ".npz")
    return sorted(
        path
        for path in tracked
        if path.endswith(forbidden_suffixes)
        or (path.startswith("data/") and not path.startswith("data/fixtures/"))
    )


def check_documents(root: Path) -> dict:
    failures: list[str] = []
    findings: list[str] = []
    source = source_release_integrity(root)
    if source["failures"]:
        failures.extend(f"SOURCE_RELEASE:{row['path']}" for row in source["failures"])
    if source["sourceRegistryDuplicateIds"]:
        findings.append(f"SOURCE_REGISTRY_DUPLICATE_IDS:{source['sourceRegistryDuplicateIds']}")
    registry_path = root / "docs/11_release/ARTIFACT_REGISTRY.csv"
    if not registry_path.is_file():
        failures.append("ARTIFACT_REGISTRY_MISSING")
        rows = []
    else:
        rows = list(csv.DictReader(registry_path.open(encoding="utf-8-sig")))
    ids = [row["artifactId"] for row in rows]
    if len(ids) != len(set(ids)):
        failures.append("ARTIFACT_ID_NOT_UNIQUE")
    for row in rows:
        path = root / row["path"]
        if not path.is_file():
            failures.append(f"ARTIFACT_MISSING:{row['path']}")
        elif sha256_path(path) != row["sha256"]:
            failures.append(f"ARTIFACT_SHA_MISMATCH:{row['path']}")
    failures.extend(f"BROKEN_REFERENCE:{value}" for value in _broken_links(root))

    expected = build_generated_documents(root)
    for relative in GENERATED_PATHS:
        path = root / relative
        if not path.is_file() or path.read_bytes() != expected[relative]:
            failures.append(f"GENERATED_DOCUMENTS_STALE:{relative}")

    status_path = root / "docs/00_master/P4_IMPLEMENTATION_STATUS.yaml"
    if status_path.is_file():
        implementation = yaml.safe_load(status_path.read_text(encoding="utf-8"))
        for gate, status in implementation.get("gates", {}).items():
            if status not in VALID_GATE_STATUS:
                failures.append(f"INVALID_GATE_STATUS:{gate}:{status}")
    trace_path = root / "docs/00_master/P4_TRACEABILITY_MATRIX.csv"
    if trace_path.is_file():
        traces = list(csv.DictReader(trace_path.open(encoding="utf-8-sig")))
        relations = {(row["sourceId"], row["relationType"]) for row in traces}
        required = {
            ("RQ-001", "MEASURED_BY"),
            ("RQ-001", "COMPUTED_IN"),
            ("RQ-002A", "MEASURED_BY"),
            ("DATA-LKA-001", "INGESTED_BY"),
            ("TAXONOMY-REQUIREMENT", "NORMALIZES"),
            ("RESULT-RQ1-*", "SUPPORTS"),
        }
        for missing in sorted(required - relations):
            failures.append(f"TRACEABILITY_MISSING:{missing[0]}:{missing[1]}")
    tracked_empirical = _tracked_empirical(root)
    failures.extend(f"TRACKED_EMPIRICAL_BYTES:{path}" for path in tracked_empirical)
    contract_text = (root / "contracts/v2.1.3_bridge/p4_contract.yaml").read_text(encoding="utf-8")
    if re.search(r"^\s+validPostingFlag:", contract_text, re.MULTILINE):
        failures.append("FORBIDDEN_CANONICAL_FIELD:validPostingFlag")
    high_demand = re.search(
        r"highDemandScore:\s*\n(?:\s+.*\n){0,6}?\s+requiredValue:\s*([^\n]+)", contract_text
    )
    if high_demand and high_demand.group(1).strip().lower() not in {"null", "none", "~"}:
        failures.append("HIGH_DEMAND_SCORE_NON_NULL_DEFINITION")
    status = "FAIL" if failures else "PASS_WITH_FINDINGS" if findings else "PASS"
    return {
        "status": status,
        "sourceRelease": source,
        "artifactCount": len(rows),
        "failures": failures,
        "findings": findings,
        "trackedEmpiricalBytes": tracked_empirical,
    }
