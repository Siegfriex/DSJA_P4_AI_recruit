from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

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
