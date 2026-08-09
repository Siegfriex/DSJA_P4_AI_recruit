from __future__ import annotations

import json
from pathlib import Path

from p4.io.hashing import sha256_file


def write_result_manifest(
    result_files: list[Path], destination: Path, *, analysis_ready: bool
) -> dict:
    if not analysis_ready:
        raise ValueError("ANALYSIS_READY_REQUIRED")
    payload = {
        "status": "ARTICLE_RESULT_READY",
        "files": [{"path": path.name, "sha256": sha256_file(path)} for path in result_files],
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
