from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_units(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    if len(frame) != 13_442:
        raise ValueError(f"NCS_UNIT_COUNT_DRIFT: {len(frame)}")
    if "ncsUnitCode" not in frame.columns:
        raise ValueError("NCS_UNIT_CODE_MISSING")
    if frame["ncsUnitCode"].isna().any() or frame["ncsUnitCode"].duplicated().any():
        raise ValueError("NCS_UNIT_CODE_INTEGRITY_FAILURE")
    return frame
