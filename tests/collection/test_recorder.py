from __future__ import annotations

import gzip
import json
from pathlib import Path

from p4.collection.recorder import record_response


def test_recorder_writes_reproducible_gzip_and_redacted_url(tmp_path: Path) -> None:
    destination = tmp_path / "object.html.gz"
    metadata = tmp_path / "object.json"
    result = record_response(
        b"<html>fixture</html>",
        destination,
        metadata,
        "https://linkareer.com/activity/1?token=secret",
    )
    assert gzip.decompress(destination.read_bytes()) == b"<html>fixture</html>"
    assert result["sourceUrl"] == "https://linkareer.com/activity/1"
    assert json.loads(metadata.read_text())["compressedSha256"] == result["compressedSha256"]
