from __future__ import annotations

import pytest

from p4.config import Settings


def test_bootstrap_defaults_are_network_free(monkeypatch) -> None:
    for name in (
        "P4_RUN_MODE",
        "P4_NETWORK_ENABLED",
        "P4_DATA_ROOT",
        "P4_ARTIFACT_ROOT",
        "P4_OBSERVED_SOURCE_ROOT",
        "P4_REPLAY_OUTPUT_ROOT",
        "P4_NCS_UNIT_PATH",
        "P4_APPROVAL_FILE",
    ):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_env()
    assert settings.run_mode == "bootstrap"
    assert settings.network_enabled is False
    assert settings.data_root == settings.root / "data"


def test_observed_mode_rejects_network(monkeypatch) -> None:
    monkeypatch.setenv("P4_RUN_MODE", "observed")
    monkeypatch.setenv("P4_NETWORK_ENABLED", "true")
    with pytest.raises(ValueError, match="network can be enabled only"):
        Settings.from_env()


def test_invalid_boolean_fails_before_stage_execution(monkeypatch) -> None:
    monkeypatch.setenv("P4_NETWORK_ENABLED", "yes")
    with pytest.raises(ValueError, match="must be true or false"):
        Settings.from_env()
