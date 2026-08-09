from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def input_artifact_sha(root: Path, excluded: set[str]) -> str:
    digest = hashlib.sha256()
    roots = ("src", "tests", "config", "contracts", "scripts", "docs", "data/fixtures")
    files: list[Path] = []
    for name in roots:
        base = root / name
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file())
    for name in ("pyproject.toml", "uv.lock", ".python-version", ".gitignore"):
        path = root / name
        if path.is_file():
            files.append(path)
    for path in sorted(set(files)):
        relative = path.relative_to(root).as_posix()
        if relative in excluded or any(
            part in {"__pycache__", ".pytest_cache", ".ruff_cache"} for part in path.parts
        ):
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
