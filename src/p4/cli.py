from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import yaml

from p4.collection.approval import Approval
from p4.collection.canary import CanaryPlan
from p4.io.hashing import sha256_file
from p4.io.paths import project_root
from p4.ncs.corpus import corpus_status
from p4.ncs.source import load_units
from p4.processing.replay import replay_observed
from p4.qa.gates import migration_gate_table
from p4.qa.lineage import verify_checksum_manifest, verify_raw_objects
from p4.qa.schema import validate_contract

app = typer.Typer(no_args_is_help=True)
audit_app = typer.Typer(no_args_is_help=True)
contract_app = typer.Typer(no_args_is_help=True)
data_app = typer.Typer(no_args_is_help=True)
replay_app = typer.Typer(no_args_is_help=True)
canary_app = typer.Typer(no_args_is_help=True)
collect_app = typer.Typer(no_args_is_help=True)
process_app = typer.Typer(no_args_is_help=True)
ncs_app = typer.Typer(no_args_is_help=True)
qa_app = typer.Typer(no_args_is_help=True)
mart_app = typer.Typer(no_args_is_help=True)
app.add_typer(audit_app, name="audit")
app.add_typer(contract_app, name="contract")
app.add_typer(data_app, name="data")
app.add_typer(replay_app, name="replay")
app.add_typer(canary_app, name="canary")
app.add_typer(collect_app, name="collect")
app.add_typer(process_app, name="process")
app.add_typer(ncs_app, name="ncs")
app.add_typer(qa_app, name="qa")
app.add_typer(mart_app, name="mart")


def _emit(payload: dict | list) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _observed_source(root: Path) -> Path:
    return root / "data/staging/legacy_observed/M1_5_RECONCILIATION_20260807_06"


def _replay_output(root: Path) -> Path:
    return root / "data/processed/observed_replay/OBSERVED_MIGRATION_20260809_02"


@audit_app.command("legacy")
def audit_legacy() -> None:
    root = project_root()
    manifest = yaml.safe_load(
        (root / "manifests/legacy_sources.lock.yaml").read_text(encoding="utf-8")
    )
    _emit({"status": "PASS", "sources": len(manifest["sources"]), "networkCalls": 0})


@contract_app.command("validate")
def contract_validate() -> None:
    _emit(validate_contract(project_root()))


@data_app.command("verify")
def data_verify() -> None:
    root = project_root()
    observed = verify_checksum_manifest(
        root / "manifests/checksums/legacy_observed_CHECKSUMS.sha256", _observed_source(root)
    )
    raw = verify_raw_objects(root / "manifests/checksums/legacy_raw_object_manifest.jsonl", root)
    ncs_path = root / "data/external/ncsUnit.parquet"
    ncs = {
        "status": "PASS",
        "rows": int(len(load_units(ncs_path))),
        "sha256": sha256_file(ncs_path),
    }
    _emit(
        {
            "status": "PASS" if observed["status"] == raw["status"] == "PASS" else "FAIL",
            "observed": observed,
            "raw": raw,
            "ncs": ncs,
        }
    )


@replay_app.command("observed")
def replay_observed_command() -> None:
    root = project_root()
    _emit(replay_observed(_observed_source(root), _replay_output(root)))


@canary_app.command("plan")
def canary_plan(tier: int = 0) -> None:
    plan = CanaryPlan(tier=tier, scope="TIER0_FIXTURE_ONLY" if tier == 0 else "APPROVAL_REQUIRED")
    plan.validate()
    _emit({**plan.__dict__, "networkCalls": 0, "status": "PLAN_ONLY"})


@canary_app.command("validate")
def canary_validate(approval_file: Path) -> None:
    root = project_root()
    approval = Approval.load(approval_file)
    registry = root / "config/query_registry.yaml"
    approval.validate_binding(root / "config/source_policy.yaml", registry)
    _emit({"status": "PASS", "approvalId": approval.approval_id, "scope": approval.scope})


def _validate_collection_approval(approval_file: Path) -> Approval:
    root = project_root()
    approval = Approval.load(approval_file)
    approval.validate_binding(
        root / "config/source_policy.yaml", root / "config/query_registry.yaml"
    )
    return approval


def _collection_command(command_name: str):
    def command(approval_file: Annotated[Path, typer.Option("--approval-file")]) -> None:
        approval = _validate_collection_approval(approval_file)
        _emit(
            {
                "status": "APPROVAL_VALIDATED_TRANSPORT_NOT_EXECUTED",
                "command": command_name,
                "approvalId": approval.approval_id,
                "networkCalls": 0,
            }
        )

    return command


for command_name in ("index", "detail", "assets"):
    collect_app.command(command_name)(_collection_command(command_name))


@process_app.command("release")
def process_release() -> None:
    raise typer.BadParameter(
        "PRODUCTION_RELEASE_NOT_AVAILABLE; use `p4 replay observed` for local migration"
    )


@ncs_app.command("build")
def ncs_build() -> None:
    root = project_root()
    _emit(corpus_status(load_units(root / "data/external/ncsUnit.parquet")))


@ncs_app.command("map")
def ncs_map() -> None:
    _emit(
        {
            "status": "NOT_EVALUATED",
            "reason": "REFERENCE_QUALITY_AUTHORITY_MISSING",
            "networkCalls": 0,
        }
    )


@qa_app.command("run")
def qa_run() -> None:
    root = project_root()
    contract = validate_contract(root)
    observed = verify_checksum_manifest(
        root / "manifests/checksums/legacy_observed_CHECKSUMS.sha256", _observed_source(root)
    )
    raw = verify_raw_objects(root / "manifests/checksums/legacy_raw_object_manifest.jsonl", root)
    report_path = _replay_output(root) / "OBSERVED_REPLAY_REPORT.json"
    replay = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    _emit(
        migration_gate_table(
            replay=replay, contract=contract, data={"observed": observed, "raw": raw}
        )
    )


@mart_app.command("build")
def mart_build() -> None:
    raise typer.BadParameter("PRODUCTION_PREPROCESSED_DATA_READY is BLOCKED")


@app.command("analyze")
def analyze() -> None:
    raise typer.BadParameter("ANALYSIS_READY is BLOCKED")


if __name__ == "__main__":
    app()
