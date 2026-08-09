from __future__ import annotations


def calibration_status(reference_rows: int, external_gold_rows: int) -> dict:
    if reference_rows == 0 or external_gold_rows == 0:
        return {"status": "NOT_EVALUATED", "precision": None, "coverage": None}
    return {"status": "IMPLEMENTED_NOT_RUN", "precision": None, "coverage": None}
