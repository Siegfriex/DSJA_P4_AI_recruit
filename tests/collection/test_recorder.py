from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from p4.collection.recorder import record_response


def test_recorder_writes_complete_reproducible_manifest(tmp_path: Path) -> None:
    destination = tmp_path / "raw" / "object.html.gz"
    metadata = tmp_path / "raw" / "object.json"
    content = b"<html>fixture</html>"
    result = record_response(
        content,
        destination,
        metadata,
        "https://linkareer.com/activity/1?token=secret",
        raw_posting_id="RAW-1",
        source_posting_id="1",
        operation="DetailPage",
        period="2026-01",
        storage_root=tmp_path,
    )
    assert gzip.decompress(destination.read_bytes()) == content
    assert result["sourceUrl"] == "https://linkareer.com/activity/1"
    assert result["contentSha256"] == hashlib.sha256(content).hexdigest()
    assert result["objectLocatorRelative"] == "raw/object.html.gz"
    assert result["byteCount"] == destination.stat().st_size
    assert json.loads(metadata.read_text())["compressedSha256"] == result["compressedSha256"]
