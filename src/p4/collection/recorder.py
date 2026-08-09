from __future__ import annotations

import gzip
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from p4.io.hashing import sha256_file


def record_response(
    content: bytes,
    destination: Path,
    metadata_path: Path,
    source_url: str,
    *,
    raw_posting_id: str,
    source_posting_id: str,
    operation: str,
    period: str,
    storage_root: Path | None = None,
) -> dict:
    """Write deterministic gzip bytes and a complete, redacted raw manifest row."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as raw_stream:
        with gzip.GzipFile(fileobj=raw_stream, mode="wb", mtime=0) as stream:
            stream.write(content)
    redacted_url = source_url.split("?", 1)[0]
    locator = destination.relative_to(storage_root) if storage_root else destination
    manifest = {
        "rawPostingId": raw_posting_id,
        "sourcePostingId": source_posting_id,
        "operation": operation,
        "period": period,
        "objectLocatorRelative": locator.as_posix(),
        "byteCount": destination.stat().st_size,
        "compressedSha256": sha256_file(destination),
        "contentByteCount": len(content),
        "contentSha256": hashlib.sha256(content).hexdigest(),
        "sourceUrl": redacted_url,
        "sourceUrlFingerprint": hashlib.sha256(redacted_url.encode()).hexdigest(),
        "retrievedAtUtc": datetime.now(UTC).isoformat(),
        "availabilityStatus": "AVAILABLE",
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
