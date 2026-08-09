from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = {
    "00_ProjectAudit.ipynb": (
        "Pure bootstrap audit",
        "!p4 env check\n!p4 contract validate\n!p4 data verify\n!p4 status",
    ),
    "01_ObservedReplay.ipynb": (
        "Observed import template",
        "!p4 data verify\n# Configure observed mode before running p4 replay observed.",
    ),
    "02_CanaryPreflight.ipynb": ("Fixture-only canary planning", "!p4 canary plan --tier 0"),
    "03_CollectRelease.ipynb": (
        "Approval-bound production collection",
        "# Transport orchestration is not implemented.\n"
        "# COLLECTION_IMPLEMENTATION_READY remains BLOCKED.",
    ),
    "04_ProcessCorpus.ipynb": (
        "Production processing orchestration",
        "# Requires PRODUCTION_PREPROCESSED_DATA_READY.",
    ),
    "05_SemanticFeatures.ipynb": ("Requirement and career-access semantic QA", "!p4 qa run"),
    "06_NcsMapping.ipynb": (
        "Local NCS corpus and mapping boundary",
        "# Configure P4_NCS_UNIT_PATH before p4 ncs build.\n!p4 ncs map",
    ),
    "07_DataQaAndMarts.ipynb": (
        "Structural and semantic QA before marts",
        "!p4 qa run\n# p4 mart build remains fail-closed.",
    ),
    "08_RqAnalysis.ipynb": (
        "RQ analysis gate",
        "# p4 analyze remains blocked until empirical gates pass.",
    ),
}


def main() -> None:
    target = ROOT / "notebooks"
    target.mkdir(exist_ok=True)
    for filename, (title, code) in NOTEBOOKS.items():
        code_lines = code.splitlines()
        payload = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {title}\n",
                        "\n",
                        "This notebook is an orchestration and audit view; "
                        "logic lives in `src/p4`.\n",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        line + ("\n" if index < len(code_lines) - 1 else "")
                        for index, line in enumerate(code_lines)
                    ],
                },
            ],
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.12"},
                "p4": {
                    "repositoryState": "PURE_BOOTSTRAP",
                    "runMode": "SOURCE_ONLY",
                    "networkCalls": 0,
                },
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        (target / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
