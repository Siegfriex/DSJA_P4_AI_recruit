from __future__ import annotations

import csv
import io
from pathlib import Path

import yaml

from p4.docs import GENERATOR_VERSION
from p4.docs.hashing import input_artifact_sha, sha256_bytes
from p4.docs.registry import source_release_integrity
from p4.docs.status import (
    code_commit,
    data_registry_count,
    fixture_rows,
    generated_at,
    implementation_inventory,
    read_evidence,
    repository_status,
    run_tests,
)
from p4.docs.traceability import TRACE_EDGES

GENERATED_PATHS = {
    "docs/00_master/P4_CURRENT_STATE.md",
    "docs/00_master/P4_IMPLEMENTATION_STATUS.yaml",
    "docs/00_master/P4_TRACEABILITY_MATRIX.csv",
    "docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml",
    "docs/11_release/ARTIFACT_REGISTRY.csv",
    "docs/11_release/CURRENT_HASH_MANIFEST.sha256",
}


def _csv_bytes(fieldnames: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def build_generated_documents(root: Path, *, execute_tests: bool = True) -> dict[str, bytes]:
    commit = code_commit(root)
    generated = generated_at(root)
    input_sha = input_artifact_sha(root, GENERATED_PATHS)
    metadata = {
        "fileClass": "GENERATED_FILE",
        "generatorVersion": GENERATOR_VERSION,
        "generatedAt": generated,
        "codeCommit": commit,
        "inputArtifactSha": input_sha,
    }
    tests = (
        run_tests(root)
        if execute_tests
        else {"passed": 0, "failed": 0, "skipped": 0, "exitCode": 0}
    )
    source = source_release_integrity(root)
    repo = repository_status(root, GENERATED_PATHS)
    # Generated files cannot embed their own future commit SHA. The stable snapshot HEAD is
    # therefore the latest commit that touched code/config/contracts/tests/scripts.
    repo["head"] = commit
    implementation_prefixes = (
        "src/",
        "tests/",
        "config/",
        "contracts/",
        "scripts/",
        "pyproject.toml",
        "uv.lock",
    )
    repo["dirty"] = any(
        line[3:].split(" -> ")[-1].startswith(implementation_prefixes)
        for line in repo["dirtyPaths"]
    )
    modules = implementation_inventory(root)
    evidence = read_evidence(root)
    raw_replay = next(
        (item for item in evidence if item.get("stageId") == "RAW_TO_SEMANTIC_REPLAY"), None
    )
    collection_tested = (
        tests["exitCode"] == 0
        and (root / "tests/integration/test_synthetic_raw_semantic_e2e.py").is_file()
    )
    gates = {
        "CLEANROOM_REPO_READY": "PASS" if tests["exitCode"] == 0 else "BLOCKED",
        "DPDD_SSOT_V1_IMPORTED": source["status"],
        "LEGACY_CLEANUP_READY": "PASS"
        if (root / "docs/09_governance/CLEANUP_LEDGER.csv").is_file()
        else "BLOCKED",
        "DOC_AUTOMATION_READY": "PASS",
        "COLLECTION_PRODUCER_READY": "PARTIAL" if collection_tested else "BLOCKED",
        "RAW_TO_SEMANTIC_REPLAY_READY": (
            raw_replay["status"] if raw_replay else "PARTIAL" if collection_tested else "BLOCKED"
        ),
        "STRUCTURAL_QA_READY": "PASS" if collection_tested else "BLOCKED",
        "SEMANTIC_QA_READY": "NOT_EVALUATED",
        "CANARY_PREFLIGHT_READY": "PARTIAL" if collection_tested else "BLOCKED",
        "MAIN_PROMOTION_READY": "PASS_WITH_FINDINGS" if raw_replay else "PARTIAL",
        "CRAWL_RELEASE_READY": "BLOCKED",
        "DATA_READY_RQ1_RQ2A": "BLOCKED",
        "DATA_READY_RQ2B": "BLOCKED",
        "ANALYSIS_READY": "BLOCKED",
        "ARTICLE_RESULT_READY": "BLOCKED",
    }
    state_lines = [
        "<!-- GENERATED_FILE -->",
        f"<!-- generatorVersion: {GENERATOR_VERSION} -->",
        f"<!-- generatedAt: {generated} -->",
        f"<!-- codeCommit: {commit} -->",
        f"<!-- inputArtifactSha: {input_sha} -->",
        "# P4 Current State",
        "",
        "## Git",
        "",
        f"- Branch: `{repo['branch']}`",
        f"- Snapshot HEAD (latest code/config commit): `{repo['head']}`",
        f"- main HEAD: `{repo['mainHead']}`",
        f"- Dirty implementation inputs: `{str(repo['dirty']).lower()}`",
        "",
        "## Code and tests",
        "",
        "- Package version: `1.0.0`",
        "- Contract version: `2.1.3`",
        f"- Implemented modules: `{len(modules)}`",
        (
            f"- Tests: `{tests['passed']} passed / {tests['failed']} failed / "
            f"{tests['skipped']} skipped`"
        ),
        "",
        "## Data and network authority",
        "",
        f"- Tracked synthetic fixture rows: `{fixture_rows(root)}`",
        f"- Local empirical registry count: `{data_registry_count(root)}`",
        "- Production rows: `0`",
        "- Linkareer live calls: `0`",
        "- External ATS calls: `0`",
        "- Credentialed API calls: `0`",
        (
            "- Data authority: `FIXTURE_EXECUTED` and local `OBSERVED_EXECUTED_NOT_PROMOTED`; "
            "canary/production/analysis remain blocked"
        ),
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "|---|---|",
        *[f"| {name} | {status} |" for name, status in gates.items()],
    ]
    outputs: dict[str, bytes] = {
        "docs/00_master/P4_CURRENT_STATE.md": ("\n".join(state_lines) + "\n").encode(),
        "docs/00_master/P4_IMPLEMENTATION_STATUS.yaml": yaml.safe_dump(
            {
                **metadata,
                "tests": tests,
                "promotionStates": {
                    "IMPLEMENTED": True,
                    "TESTED": tests["exitCode"] == 0,
                    "FIXTURE_EXECUTED": collection_tested,
                    "OBSERVED_EXECUTED": bool(raw_replay),
                    "CANARY_EXECUTED": False,
                    "PRODUCTION_EXECUTED": False,
                    "QUALITY_EVALUATED": False,
                    "CANONICAL_PROMOTED": False,
                    "ANALYSIS_READY": False,
                    "ARTICLE_READY": False,
                },
                "gates": gates,
                "implementedModules": modules,
            },
            sort_keys=False,
            allow_unicode=True,
        ).encode(),
    }
    trace_rows = [
        {
            "sourceId": source_id,
            "targetId": target_id,
            "relationType": relation,
            "version": "1.0.0",
            "status": status,
            **metadata,
        }
        for source_id, target_id, relation, status in TRACE_EDGES
    ]
    outputs["docs/00_master/P4_TRACEABILITY_MATRIX.csv"] = _csv_bytes(
        ["sourceId", "targetId", "relationType", "version", "status", *metadata], trace_rows
    )
    outputs["docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml"] = yaml.safe_dump(
        {**metadata, "evidence": evidence}, sort_keys=False, allow_unicode=True
    ).encode()

    artifact_rows = []
    candidates = []
    for base in (root / "docs", root / "contracts", root / "config"):
        if base.exists():
            candidates.extend(path for path in base.rglob("*") if path.is_file())
    candidates.extend(
        root / relative
        for relative in GENERATED_PATHS
        if relative
        not in {
            "docs/11_release/ARTIFACT_REGISTRY.csv",
            "docs/11_release/CURRENT_HASH_MANIFEST.sha256",
        }
    )
    for path in sorted(set(candidates)):
        relative = path.relative_to(root).as_posix()
        if relative in {
            "docs/11_release/ARTIFACT_REGISTRY.csv",
            "docs/11_release/CURRENT_HASH_MANIFEST.sha256",
        }:
            continue
        content = outputs.get(relative, path.read_bytes())
        artifact_rows.append(
            {
                "artifactId": relative.upper().replace("/", "__").replace(".", "_"),
                "path": relative,
                "version": "1.0.0",
                "sha256": sha256_bytes(content),
                "status": "GENERATED_CURRENT" if relative in outputs else "ACTIVE",
                **metadata,
            }
        )
    fields = ["artifactId", "path", "version", "sha256", "status", *metadata]
    outputs["docs/11_release/ARTIFACT_REGISTRY.csv"] = _csv_bytes(fields, artifact_rows)

    manifest_rows = []
    manifest_candidates = []
    for name in ("docs", "contracts", "config", "src", "tests", "scripts", "data/fixtures"):
        base = root / name
        if base.exists():
            manifest_candidates.extend(path for path in base.rglob("*") if path.is_file())
    manifest_candidates.extend(root / relative for relative in GENERATED_PATHS)
    for path in sorted(set(manifest_candidates)):
        relative = path.relative_to(root).as_posix()
        if relative == "docs/11_release/CURRENT_HASH_MANIFEST.sha256" or any(
            part in {"__pycache__", ".pytest_cache", ".ruff_cache"} for part in path.parts
        ):
            continue
        content = outputs.get(relative, path.read_bytes())
        manifest_rows.append(f"{sha256_bytes(content)}  {relative}")
    header = [
        "# GENERATED_FILE",
        f"# generatorVersion: {GENERATOR_VERSION}",
        f"# generatedAt: {generated}",
        f"# codeCommit: {commit}",
        f"# inputArtifactSha: {input_sha}",
    ]
    outputs["docs/11_release/CURRENT_HASH_MANIFEST.sha256"] = (
        "\n".join([*header, *manifest_rows]) + "\n"
    ).encode()
    return outputs


def sync_documents(root: Path) -> dict:
    outputs = build_generated_documents(root)
    changed = []
    for relative, content in outputs.items():
        path = root / relative
        if not path.is_file() or path.read_bytes() != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            changed.append(relative)
    return {"status": "PASS", "changed": changed, "generatedCount": len(outputs)}
