from __future__ import annotations

import gzip
import json
from datetime import UTC, datetime
from pathlib import Path

from p4.io.hashing import sha256_file


def record_response(
    content: bytes, destination: Path, metadata_path: Path, source_url: str
) -> dict:
    """Write content-addressed gzip bytes and redacted lineage metadata."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as raw_stream:
        stream = gzip.GzipFile(fileobj=raw_stream, mode="wb", mtime=0)
        stream.write(content)
        stream.close()
    manifest = {
        "objectLocatorRelative": destination.as_posix(),
        "compressedSha256": sha256_file(destination),
        "contentByteCount": len(content),
        "sourceUrl": source_url.split("?", 1)[0],
        "retrievedAtUtc": datetime.now(UTC).isoformat(),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
