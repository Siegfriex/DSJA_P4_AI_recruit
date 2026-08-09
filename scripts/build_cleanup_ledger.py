from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "d691a97d68b237ef0698c36a3576cdbb07b6c29d"


def classify(path: str) -> tuple[str, str, str, str]:
    if path.startswith("docs/"):
        return (
            "ARCHIVE_EXTERNAL",
            "superseded migration-era documentation",
            "docs/00_master through docs/11_release",
            "not imported; preserved in Git bundle archive",
        )
    if path.startswith("notebooks/") or path == "scripts/generate_notebooks.py":
        return (
            "DROP_OBSOLETE",
            "output-free migration scaffold without producer evidence",
            "notebooks/README.md",
            "drop unless tied to an executable contract",
        )
    if path.startswith("env/"):
        if path in {"env/README.md", "env/fixture.env.example", "env/observed.env.example"}:
            return (
                "KEEP_CANONICAL",
                "secret-free environment profile retained with network disabled",
                "env/README.md and env/*-replay.env.example",
                "REFACTOR",
            )
        return (
            "DROP_OBSOLETE",
            "approval-bearing canary or production profile is not valid in cleanroom phase",
            ".env.example and network-free env profiles",
            "do not import",
        )
    if path.startswith("data/") and path != "data/fixtures/README.md":
        return (
            "DROP_OBSOLETE",
            "empty lifecycle placeholder outside canonical tracked fixture scope",
            "data/fixtures",
            "do not import",
        )
    if (
        "AGENT3_TO_AGENT" in path
        or path.endswith("QUALITY_GATES.md")
        or path.endswith("SOURCE_POLICY_GATE.md")
    ):
        return (
            "ARCHIVE_EXTERNAL",
            "stale agent or migration handoff report",
            "DPDD governance and validation specs",
            "preserved in archive only",
        )
    if path.startswith("contracts/v2.1.2_legacy/"):
        return (
            "KEEP_COMPATIBILITY",
            "2.1.2 compatibility contract required by 2.1.3 bridge validation",
            path,
            "selective import",
        )
    if path.startswith("contracts/"):
        return (
            "KEEP_CANONICAL",
            "current bridge contract or extension schema",
            path,
            "selective import",
        )
    if path == "src/p4/processing/replay.py":
        return (
            "DROP_OBSOLETE",
            "depends on legacy precomputed semantic tables",
            "src/p4/processing/producers.py",
            "replace with raw-to-semantic producer",
        )
    if path in {"src/p4/ncs/calibration.py", "src/p4/ncs/evaluation.py"}:
        return (
            "DROP_OBSOLETE",
            "status-only skeleton without evaluation capability",
            "future Contract 2.4 implementation",
            "not promoted as implemented",
        )
    if path in {"src/p4/qa/gates.py", "src/p4/qa/semantics.py"}:
        return (
            "DROP_OBSOLETE",
            "status-only bootstrap wrapper replaced by evidence-derived QA",
            "src/p4/qa/bundle.py and src/p4/docs/status.py",
            "drop",
        )
    if path == "tests/integration/test_empty_bootstrap.py":
        return (
            "DROP_OBSOLETE",
            "pure-bootstrap assertion superseded by cleanroom synthetic E2E",
            "tests/integration/test_synthetic_raw_semantic_e2e.py",
            "drop",
        )
    if path.startswith("src/p4/collection/"):
        action = "KEEP" if path.endswith(("assets.py", "detail.py", "__init__.py")) else "REFACTOR"
        return (
            "KEEP_CANONICAL",
            "bounded collection primitive selected after code audit",
            path,
            action,
        )
    if path.startswith("src/p4/"):
        return (
            "KEEP_CANONICAL",
            "selected implementation base; governed by new tests and docs",
            path,
            "REFACTOR" if path.endswith(("cli.py", "config.py")) else "KEEP",
        )
    if path.startswith("tests/"):
        return (
            "KEEP_CANONICAL",
            "network-free regression test selected for cleanroom",
            path,
            "REFACTOR",
        )
    if path.startswith("manifests/checksums/") or path == "manifests/legacy_sources.lock.yaml":
        return (
            "ARCHIVE_EXTERNAL",
            "migration-specific generated provenance",
            "docs/09_governance/CLEANUP_LEDGER.csv",
            "preserved in archive only",
        )
    if path.startswith("artifacts/"):
        return (
            "DELETE_GENERATED",
            "generated evidence location contains placeholders only",
            "artifacts/.gitkeep",
            "normalize",
        )
    if path.startswith(".github/"):
        return (
            "KEEP_CANONICAL",
            "CI retained but rewritten for DPDD governance",
            path,
            "REWRITE",
        )
    if path in {"README.md", ".env.example", ".gitignore"} or path.startswith("config/"):
        return (
            "KEEP_CANONICAL",
            "repository control retained with cleanroom semantics",
            path,
            "REWRITE",
        )
    return ("KEEP_CANONICAL", "required build or project metadata", path, "KEEP")


def main() -> int:
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", SOURCE_COMMIT], cwd=ROOT, text=True
    ).splitlines()
    destination = ROOT / "docs/09_governance/CLEANUP_LEDGER.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            [
                "legacy_path",
                "classification",
                "reason",
                "replacement",
                "source_commit",
                "sha256",
                "action",
            ]
        )
        for path in files:
            content = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT)
            classification, reason, replacement, action = classify(path)
            writer.writerow(
                [
                    path,
                    classification,
                    reason,
                    replacement,
                    SOURCE_COMMIT,
                    hashlib.sha256(content).hexdigest(),
                    action,
                ]
            )
    print(f"PASS: cleanup ledger rows={len(files)} sourceCommit={SOURCE_COMMIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
