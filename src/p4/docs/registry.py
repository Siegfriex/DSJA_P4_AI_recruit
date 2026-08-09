from __future__ import annotations

import csv
from pathlib import Path

import yaml

from p4.docs.hashing import sha256_path

SOURCE_RELEASE = "P4-DPDD-SSOT-1.0.0"
SOURCE_SPECIAL_PATHS = {
    "00_master/P4_RELEASE_MANIFEST.yaml": (
        "11_release/source_v1.0.0/P4_RELEASE_MANIFEST_v1.0.0.yaml"
    ),
    "00_master/P4_TRACEABILITY_MATRIX.csv": (
        "11_release/source_v1.0.0/P4_TRACEABILITY_MATRIX_v1.0.0.csv"
    ),
    "11_release/ARTIFACT_REGISTRY.csv": ("11_release/source_v1.0.0/ARTIFACT_REGISTRY_v1.0.0.csv"),
}


def source_release_integrity(root: Path) -> dict:
    docs = root / "docs"
    release_path = docs / "11_release/source_v1.0.0/P4_RELEASE_MANIFEST_v1.0.0.yaml"
    evidence_path = docs / "11_release/source_v1.0.0/EVIDENCE_MANIFEST_v1.0.0.sha256"
    release = yaml.safe_load(release_path.read_text(encoding="utf-8"))
    evidence: dict[str, str] = {}
    for line in evidence_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            expected, relative = line.split(maxsplit=1)
            evidence[relative.strip().lstrip("*")] = expected
    failures: list[dict[str, str]] = []
    for relative, expected in evidence.items():
        mapped = SOURCE_SPECIAL_PATHS.get(relative, relative)
        path = docs / mapped
        actual = sha256_path(path) if path.is_file() else "MISSING"
        if actual != expected:
            failures.append({"path": relative, "expected": expected, "actual": actual})
    imports = release.get("imports", [])
    for item in imports:
        relative = item["path"]
        mapped = SOURCE_SPECIAL_PATHS.get(relative, relative)
        path = docs / mapped
        actual = sha256_path(path) if path.is_file() else "MISSING"
        if actual != str(item["sha256"]):
            failures.append({"path": relative, "expected": str(item["sha256"]), "actual": actual})
    source_registry = list(
        csv.DictReader(
            (docs / "11_release/source_v1.0.0/ARTIFACT_REGISTRY_v1.0.0.csv").open(
                encoding="utf-8-sig"
            )
        )
    )
    duplicate_ids = len(source_registry) - len({row["artifactId"] for row in source_registry})
    status = "FAIL" if failures else "PASS_WITH_FINDINGS" if duplicate_ids else "PASS"
    return {
        "status": status,
        "sourceReleaseId": release["release"]["releaseId"],
        "releaseVersion": str(release["release"]["releaseVersion"]),
        "importCount": len(imports),
        "evidenceCount": len(evidence),
        "failures": failures,
        "sourceRegistryDuplicateIds": duplicate_ids,
        "sourceManifestSha": sha256_path(release_path),
        "sourceEvidenceManifestSha": sha256_path(evidence_path),
    }
