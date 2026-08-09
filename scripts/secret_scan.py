from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    re.compile(r"gh[opusr]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
)


def main() -> int:
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    findings = []
    for relative in files:
        path = ROOT / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for pattern in PATTERNS:
            if pattern.search(text):
                findings.append(relative)
                break
    if findings:
        raise SystemExit("possible secrets: " + ", ".join(sorted(set(findings))))
    print(f"PASS: scanned {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
