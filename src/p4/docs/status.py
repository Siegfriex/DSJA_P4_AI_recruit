from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).rstrip()


def code_commit(root: Path) -> str:
    paths = ["src", "tests", "config", "contracts", "scripts", "pyproject.toml"]
    value = _git(root, "log", "-1", "--format=%H", "--", *paths)
    return value or _git(root, "rev-parse", "HEAD")


def generated_at(root: Path) -> str:
    commit = code_commit(root)
    return _git(root, "show", "-s", "--format=%cI", commit)


def run_tests(root: Path) -> dict[str, int]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-ra", "--disable-warnings"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout

    def count(label: str) -> int:
        match = re.search(rf"(\d+) {label}", output)
        return int(match.group(1)) if match else 0

    return {
        "passed": count("passed"),
        "failed": count("failed"),
        "skipped": count("skipped"),
        "exitCode": result.returncode,
    }


def implementation_inventory(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root / "src/p4").with_suffix("").as_posix()
        for path in (root / "src/p4").rglob("*.py")
        if path.name != "__init__.py" and "__pycache__" not in path.parts
    )


def fixture_rows(root: Path) -> int:
    rows = 0
    for path in (root / "tests/fixtures").glob("*.csv"):
        rows += max(len(path.read_text(encoding="utf-8-sig").splitlines()) - 1, 0)
    return rows


def data_registry_count(root: Path) -> int:
    path = root / "manifests/data_registry.yaml"
    if not path.is_file():
        return 0
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return len(payload.get("datasets") or {})


def repository_status(root: Path, generated_paths: set[str]) -> dict:
    dirty_rows = []
    for line in _git(root, "status", "--porcelain").splitlines():
        path = line[3:].split(" -> ")[-1]
        if path not in generated_paths:
            dirty_rows.append(line)
    try:
        main_head = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
    except subprocess.CalledProcessError:
        main_head = os.environ.get("P4_MAIN_HEAD", "UNAVAILABLE_IN_SHALLOW_CHECKOUT")
    return {
        "branch": os.environ.get("P4_BRANCH_NAME") or _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "mainHead": main_head,
        "dirty": bool(dirty_rows),
        "dirtyPaths": dirty_rows,
    }


def read_evidence(root: Path) -> list[dict]:
    entries = []
    for path in sorted((root / "docs/08_evidence").rglob("*_ATTESTATION.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "evidenceId": payload.get("evidenceId"),
                "runId": payload.get("runId"),
                "stageId": payload.get("stageId"),
                "status": payload.get("status"),
            }
        )
    return entries
