from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = []
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    if len(notebooks) != 9:
        failures.append(f"expected 9 source notebooks, found {len(notebooks)}")
    for path in notebooks:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(payload.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            if cell.get("execution_count") is not None or cell.get("outputs"):
                failures.append(f"{path.name}: cell {index} contains execution state")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(notebooks)} source notebooks are output-free")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
