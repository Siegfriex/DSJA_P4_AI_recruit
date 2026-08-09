from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def data_root() -> Path:
    configured = os.getenv("P4_DATA_ROOT")
    return Path(configured).expanduser().resolve() if configured else project_root() / "data"


def require_within(path: Path, root: Path) -> Path:
    resolved = path.expanduser().resolve()
    resolved.relative_to(root.expanduser().resolve())
    return resolved
