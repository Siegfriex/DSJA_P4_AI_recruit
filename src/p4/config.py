from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from p4.io.paths import project_root

RUN_MODES = {"bootstrap", "fixture", "observed", "canary", "production"}


def _path_from_env(name: str, default: Path, root: Path) -> Path:
    value = os.getenv(name)
    candidate = Path(value).expanduser() if value else default
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _bool_from_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"{name} must be true or false")
    return normalized == "true"


@dataclass(frozen=True)
class Settings:
    root: Path
    run_mode: str
    network_enabled: bool
    data_root: Path
    artifact_root: Path
    raw_root: Path
    staging_root: Path
    processed_root: Path
    external_root: Path
    reference_root: Path
    mart_root: Path
    release_root: Path
    observed_source_root: Path | None
    replay_output_root: Path | None
    ncs_unit_path: Path | None
    approval_file: Path | None

    @classmethod
    def from_env(cls) -> Settings:
        root = project_root()
        data_root = _path_from_env("P4_DATA_ROOT", root / "data", root)

        def optional_path(name: str) -> Path | None:
            value = os.getenv(name)
            return _path_from_env(name, root / value, root) if value else None

        settings = cls(
            root=root,
            run_mode=os.getenv("P4_RUN_MODE", "bootstrap").strip().lower(),
            network_enabled=_bool_from_env("P4_NETWORK_ENABLED"),
            data_root=data_root,
            artifact_root=_path_from_env("P4_ARTIFACT_ROOT", root / "artifacts", root),
            raw_root=_path_from_env("P4_RAW_ROOT", data_root / "raw", root),
            staging_root=_path_from_env("P4_STAGING_ROOT", data_root / "staging", root),
            processed_root=_path_from_env("P4_PROCESSED_ROOT", data_root / "processed", root),
            external_root=_path_from_env("P4_EXTERNAL_ROOT", data_root / "external", root),
            reference_root=_path_from_env("P4_REFERENCE_ROOT", data_root / "reference", root),
            mart_root=_path_from_env("P4_MART_ROOT", data_root / "marts", root),
            release_root=_path_from_env("P4_RELEASE_ROOT", data_root / "releases", root),
            observed_source_root=optional_path("P4_OBSERVED_SOURCE_ROOT"),
            replay_output_root=optional_path("P4_REPLAY_OUTPUT_ROOT"),
            ncs_unit_path=optional_path("P4_NCS_UNIT_PATH"),
            approval_file=optional_path("P4_APPROVAL_FILE"),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.run_mode not in RUN_MODES:
            raise ValueError(f"P4_RUN_MODE must be one of {sorted(RUN_MODES)}")
        if self.network_enabled and self.run_mode not in {"canary", "production"}:
            raise ValueError("network can be enabled only in canary or production mode")
        if self.run_mode in {"bootstrap", "fixture", "observed"} and self.network_enabled:
            raise ValueError(f"network must be disabled in {self.run_mode} mode")

    def path_status(self) -> dict[str, dict[str, str | bool]]:
        paths = {
            "dataRoot": self.data_root,
            "artifactRoot": self.artifact_root,
            "rawRoot": self.raw_root,
            "stagingRoot": self.staging_root,
            "processedRoot": self.processed_root,
            "externalRoot": self.external_root,
            "referenceRoot": self.reference_root,
            "martRoot": self.mart_root,
            "releaseRoot": self.release_root,
        }
        return {name: {"path": str(path), "exists": path.exists()} for name, path in paths.items()}

    def public_status(self) -> dict:
        return {
            "status": "PASS",
            "runMode": self.run_mode,
            "networkEnabled": self.network_enabled,
            "paths": self.path_status(),
            "observedSourceConfigured": self.observed_source_root is not None,
            "replayOutputConfigured": self.replay_output_root is not None,
            "ncsUnitConfigured": self.ncs_unit_path is not None,
            "approvalConfigured": self.approval_file is not None,
        }
