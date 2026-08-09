from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = (
        ROOT / "docs/SSOT.md",
        ROOT / "docs/01_SYSTEM_DESIGN_SPEC.md",
        ROOT / "docs/02_DETAILED_DESIGN.md",
        ROOT / "docs/03_IMPLEMENTATION_RUNBOOK.md",
        ROOT / "env/bootstrap.env.example",
        ROOT / "env/fixture.env.example",
        ROOT / "env/observed.env.example",
        ROOT / "env/canary.env.example",
        ROOT / "env/production.env.example",
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    registry = yaml.safe_load((ROOT / "manifests/data_registry.yaml").read_text(encoding="utf-8"))
    if registry.get("state") != "EMPTY_BOOTSTRAP" or registry.get("datasets"):
        missing.append("data registry is not EMPTY_BOOTSTRAP")
    populated = []
    for name in ("raw", "external", "staging", "processed", "reference", "marts", "releases"):
        data_root = ROOT / "data" / name
        populated.extend(
            str(path.relative_to(ROOT))
            for path in data_root.rglob("*")
            if path.is_file() and path.name != ".gitkeep"
        )
    if populated:
        missing.extend(f"populated data: {path}" for path in populated)
    if missing:
        raise SystemExit("\n".join(missing))
    print("PASS: PURE_BOOTSTRAP docs=4 env_profiles=5 active_datasets=0 populated_files=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
