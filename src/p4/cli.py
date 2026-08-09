from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import yaml

from p4.collection.approval import Approval
from p4.collection.canary import CanaryPlan
from p4.config import Settings
from p4.io.paths import project_root
from p4.ncs.corpus import corpus_status
from p4.ncs.source import load_units
from p4.processing.replay import replay_observed
from p4.qa.gates import bootstrap_gate_table
from p4.qa.lineage import verify_data_registry
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
env_app = typer.Typer(no_args_is_help=True)
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
    manifest = yaml.safe_load(
        (root / "manifests/legacy_sources.lock.yaml").read_text(encoding="utf-8")
    )
    _emit({"status": "PASS", "sources": len(manifest["sources"]), "networkCalls": 0})


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


@replay_app.command("observed")
def replay_observed_command() -> None:
    settings = Settings.from_env()
    if settings.run_mode != "observed":
        raise typer.BadParameter("P4_RUN_MODE=observed is required")
    source = _required_configured_path(settings.observed_source_root, "P4_OBSERVED_SOURCE_ROOT")
    output = _required_configured_path(settings.replay_output_root, "P4_REPLAY_OUTPUT_ROOT")
    if not source.is_dir():
        raise typer.BadParameter(f"observed source does not exist: {source}")
    _emit(replay_observed(source, output))


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
    settings = Settings.from_env()
    contract = validate_contract(settings.root)
    data = verify_data_registry(settings.root / "manifests/data_registry.yaml", settings)
    _emit(bootstrap_gate_table(root=settings.root, contract=contract, data=data))


@mart_app.command("build")
def mart_build() -> None:
    raise typer.BadParameter("PRODUCTION_PREPROCESSED_DATA_READY is BLOCKED")


@app.command("analyze")
def analyze() -> None:
    raise typer.BadParameter("ANALYSIS_READY is BLOCKED")


@app.command("status")
def status() -> None:
    settings = Settings.from_env()
    contract = validate_contract(settings.root)
    data = verify_data_registry(settings.root / "manifests/data_registry.yaml", settings)
    gates = bootstrap_gate_table(root=settings.root, contract=contract, data=data)
    bootstrap_ready = all(
        item["status"] == "PASS"
        for item in gates
        if item["gate"]
        in {
            "REPOSITORY_BOOTSTRAP_READY",
            "DESIGN_SPEC_READY",
            "CONTRACT_BRIDGE_READY",
            "ENVIRONMENT_TEMPLATE_READY",
            "DATA_INVENTORY_EMPTY",
        }
    )
    _emit(
        {
            "status": "PURE_BOOTSTRAP_READY" if bootstrap_ready else "BOOTSTRAP_BLOCKED",
            "runMode": settings.run_mode,
            "networkEnabled": settings.network_enabled,
            "data": data,
            "gates": gates,
        }
    )


if __name__ == "__main__":
    app()
