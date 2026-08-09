from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from p4.config import Settings
from p4.io.hashing import sha256_file


def verify_checksum_manifest(manifest: Path, data_root: Path) -> dict:
    checked = 0
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = data_root / relative.strip().lstrip("*")
        actual = sha256_file(path) if path.is_file() else "MISSING"
        checked += 1
        if actual != expected:
            failures.append({"path": relative, "expected": expected, "actual": actual})
    return {"status": "PASS" if not failures else "FAIL", "checked": checked, "failures": failures}


def verify_raw_objects(manifest: Path, repository_root: Path) -> dict:
    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line]
    failures = []
    for row in rows:
        locator = Path(row["objectLocatorRelative"])
        if locator.is_absolute() or ".." in locator.parts:
            failures.append({"rawPostingId": row["rawPostingId"], "reason": "UNSAFE_LOCATOR"})
            continue
        path = repository_root / locator
        if not path.is_file():
            failures.append({"rawPostingId": row["rawPostingId"], "reason": "MISSING"})
            continue
        compressed = sha256_file(path)
        with gzip.open(path, "rb") as stream:
            content = stream.read()
        content_sha = hashlib.sha256(content).hexdigest()
        if compressed != row["compressedSha256"]:
            failures.append({"rawPostingId": row["rawPostingId"], "reason": "COMPRESSED_SHA"})
        elif content_sha != row["contentSha256"]:
            failures.append({"rawPostingId": row["rawPostingId"], "reason": "CONTENT_SHA"})
        elif path.stat().st_size != row["byteCount"] or len(content) != row["contentByteCount"]:
            failures.append({"rawPostingId": row["rawPostingId"], "reason": "BYTE_COUNT"})
    return {
        "status": "PASS" if not failures else "FAIL",
        "objectCount": len(rows),
        "verifiedCount": len(rows) - len(failures),
        "failures": failures,
    }


def verify_data_registry(registry_path: Path, settings: Settings) -> dict:
    """Verify the active registry without treating a deliberate empty state as failure."""
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    datasets = registry.get("datasets") or {}
    expected_slots = registry.get("expectedSlots") or {}
    if not datasets:
        populated = []
        for root in (
            settings.raw_root,
            settings.staging_root,
            settings.processed_root,
            settings.external_root,
            settings.reference_root,
            settings.mart_root,
            settings.release_root,
        ):
            if root.is_dir():
                populated.extend(
                    str(path)
                    for path in root.rglob("*")
                    if path.is_file() and path.name != ".gitkeep"
                )
        return {
            "status": "EMPTY_BOOTSTRAP" if not populated else "UNREGISTERED_DATA_FOUND",
            "registryState": registry.get("state", "UNKNOWN"),
            "datasetCount": 0,
            "populatedFileCount": len(populated),
            "unregisteredFiles": populated,
            "expectedSlots": expected_slots,
        }

    checks = []
    for dataset_id, definition in datasets.items():
        relative = Path(definition["localPath"])
        path = relative if relative.is_absolute() else settings.root / relative
        failures = []
        if not path.is_file():
            failures.append("MISSING")
        else:
            expected_sha = definition.get("sha256")
            if expected_sha and sha256_file(path) != expected_sha:
                failures.append("SHA256_MISMATCH")
            expected_rows = definition.get("rows")
            if expected_rows is not None and path.suffix == ".parquet":
                if len(pd.read_parquet(path)) != int(expected_rows):
                    failures.append("ROW_COUNT_MISMATCH")
        checks.append(
            {
                "datasetId": dataset_id,
                "path": str(path),
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
            }
        )
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "registryState": registry.get("state", "ACTIVE"),
        "datasetCount": len(checks),
        "checks": checks,
    }
