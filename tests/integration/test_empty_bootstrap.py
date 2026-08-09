from __future__ import annotations

from typer.testing import CliRunner

from p4.cli import app


def test_data_verify_reports_deliberate_empty_bootstrap(monkeypatch) -> None:
    monkeypatch.setenv("P4_RUN_MODE", "bootstrap")
    monkeypatch.setenv("P4_NETWORK_ENABLED", "false")
    result = CliRunner().invoke(app, ["data", "verify"])
    assert result.exit_code == 0
    assert '"status": "EMPTY_BOOTSTRAP"' in result.stdout
    assert '"populatedFileCount": 0' in result.stdout


def test_status_separates_bootstrap_readiness_from_downstream_gates(monkeypatch) -> None:
    monkeypatch.setenv("P4_RUN_MODE", "bootstrap")
    monkeypatch.setenv("P4_NETWORK_ENABLED", "false")
    result = CliRunner().invoke(app, ["status"])
    assert result.exit_code == 0
    assert '"status": "PURE_BOOTSTRAP_READY"' in result.stdout
    assert '"gate": "ANALYSIS_READY"' in result.stdout
    assert '"status": "BLOCKED"' in result.stdout
