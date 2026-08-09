from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from p4.collection.approval import Approval
from p4.collection.canary import CanaryPlan
from p4.config import Settings
from p4.docs.release import release_plan
from p4.docs.status import repository_status
from p4.docs.sync import sync_documents
from p4.docs.validate import check_documents
from p4.io.paths import project_root
from p4.ncs.corpus import corpus_status
from p4.ncs.source import load_units
from p4.qa.lineage import verify_data_registry
from p4.qa.schema import validate_contract

app = typer.Typer(no_args_is_help=True)
audit_app = typer.Typer(no_args_is_help=True)
contract_app = typer.Typer(no_args_is_help=True)
data_app = typer.Typer(no_args_is_help=True)
docs_app = typer.Typer(no_args_is_help=True)
canary_app = typer.Typer(no_args_is_help=True)
collect_app = typer.Typer(no_args_is_help=True)
process_app = typer.Typer(no_args_is_help=True)
ncs_app = typer.Typer(no_args_is_help=True)
qa_app = typer.Typer(no_args_is_help=True)
mart_app = typer.Typer(no_args_is_help=True)
env_app = typer.Typer(no_args_is_help=True)
app.add_typer(audit_app, name="audit")
app.add_typer(contract_app, name="contract")
app.add_typer(data_app, name="data")
app.add_typer(docs_app, name="docs")
app.add_typer(canary_app, name="canary")
app.add_typer(collect_app, name="collect")
app.add_typer(process_app, name="process")
app.add_typer(ncs_app, name="ncs")
app.add_typer(qa_app, name="qa")
app.add_typer(mart_app, name="mart")
app.add_typer(env_app, name="env")


def _emit(payload: dict | list) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _required_configured_path(value: Path | None, variable: str) -> Path:
    if value is None:
        raise typer.BadParameter(f"{variable} is not configured")
    return value


@audit_app.command("legacy")
def audit_legacy() -> None:
    root = project_root()
    ledger = root / "docs/09_governance/CLEANUP_LEDGER.csv"
    _emit({"status": "PASS" if ledger.is_file() else "FAIL", "ledger": str(ledger)})


@contract_app.command("validate")
def contract_validate() -> None:
    _emit(validate_contract(project_root()))


@env_app.command("show")
def env_show() -> None:
    _emit(Settings.from_env().public_status())


@env_app.command("check")
def env_check() -> None:
    settings = Settings.from_env()
    payload = settings.public_status()
    payload["status"] = "PASS"
    _emit(payload)


@data_app.command("verify")
def data_verify() -> None:
    settings = Settings.from_env()
    _emit(verify_data_registry(settings.root / "manifests/data_registry.yaml", settings))


@docs_app.command("sync")
def docs_sync() -> None:
    _emit(sync_documents(project_root()))


@docs_app.command("check")
def docs_check() -> None:
    result = check_documents(project_root())
    _emit(result)
    if result["status"] == "FAIL":
        raise typer.Exit(1)


@docs_app.command("status")
def docs_status() -> None:
    root = project_root()
    generated = {
        "docs/00_master/P4_CURRENT_STATE.md",
        "docs/00_master/P4_IMPLEMENTATION_STATUS.yaml",
        "docs/00_master/P4_TRACEABILITY_MATRIX.csv",
        "docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml",
        "docs/11_release/ARTIFACT_REGISTRY.csv",
        "docs/11_release/CURRENT_HASH_MANIFEST.sha256",
    }
    _emit(repository_status(root, generated))


@docs_app.command("release")
def docs_release(bump: Annotated[str, typer.Option("--bump")] = "patch") -> None:
    _emit(release_plan(project_root(), bump))


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
        "PRODUCTION_RELEASE_NOT_AVAILABLE; raw-to-semantic execution requires an explicit run"
    )


@ncs_app.command("build")
def ncs_build() -> None:
    settings = Settings.from_env()
    path = _required_configured_path(settings.ncs_unit_path, "P4_NCS_UNIT_PATH")
    if not path.is_file():
        raise typer.BadParameter(f"NCS unit file does not exist: {path}")
    _emit(corpus_status(load_units(path)))


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
    _emit({"contract": validate_contract(root), "docs": check_documents(root)})


@mart_app.command("build")
def mart_build() -> None:
    raise typer.BadParameter("PRODUCTION_PREPROCESSED_DATA_READY is BLOCKED")


@app.command("analyze")
def analyze() -> None:
    raise typer.BadParameter("ANALYSIS_READY is BLOCKED")


@app.command("status")
def status() -> None:
    root = project_root()
    result = check_documents(root)
    _emit({"status": result["status"], "documents": result, "networkCalls": 0})


if __name__ == "__main__":
    app()
