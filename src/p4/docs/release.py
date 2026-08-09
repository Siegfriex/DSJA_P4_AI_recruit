from __future__ import annotations

from pathlib import Path

from p4.docs.hashing import sha256_path
from p4.docs.registry import source_release_integrity


def bump_version(version: str, bump: str) -> str:
    major, minor, patch = (int(part) for part in version.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("bump must be patch, minor, or major")


def release_plan(root: Path, bump: str) -> dict:
    source = source_release_integrity(root)
    current = source["releaseVersion"]
    return {
        "status": "REVIEW_REQUIRED",
        "sourceReleaseId": source["sourceReleaseId"],
        "currentVersion": current,
        "proposedVersion": bump_version(current, bump),
        "bump": bump,
        "currentHashManifestSha": sha256_path(
            root / "docs/11_release/CURRENT_HASH_MANIFEST.sha256"
        ),
        "reason": "release promotion requires explicit user approval",
    }
