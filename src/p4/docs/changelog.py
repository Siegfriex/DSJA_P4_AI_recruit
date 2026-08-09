from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def changelog_entry(root: Path, commit: str = "HEAD") -> str:
    sha = _git(root, "rev-parse", commit)
    paths = _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines()
    affected = [path for path in paths if path.startswith(("docs/", "contracts/", "config/"))]
    change_class = "REVIEW_REQUIRED"
    if paths and all(path.startswith("docs/") for path in paths):
        change_class = "DOCUMENTATION"
    return "\n".join(
        [
            f"## {datetime.now(UTC).date().isoformat()} · {sha[:12]}",
            "",
            f"- commitSha: `{sha}`",
            f"- changeClass: `{change_class}`",
            f"- affectedArtifactIds: `{', '.join(affected) if affected else 'REVIEW_REQUIRED'}`",
            f"- code paths: `{', '.join(paths) if paths else 'none'}`",
            "- contract impact: `REVIEW_REQUIRED`",
            "- data impact: `REVIEW_REQUIRED`",
            "- analysis impact: `REVIEW_REQUIRED`",
            "- required rerun: `uv run p4 docs sync && uv run p4 docs check`",
            "- gate impact: `REVIEW_REQUIRED`",
            "",
        ]
    )


def append_changelog(root: Path, commit: str = "HEAD") -> dict:
    path = root / "docs/00_master/P4_CHANGELOG.md"
    sha = _git(root, "rev-parse", commit)
    current = path.read_text(encoding="utf-8") if path.is_file() else "# P4 Changelog\n\n"
    if sha in current:
        return {"status": "UNCHANGED", "commitSha": sha}
    path.write_text(current + changelog_entry(root, commit), encoding="utf-8")
    return {"status": "PASS", "commitSha": sha, "path": path.relative_to(root).as_posix()}
