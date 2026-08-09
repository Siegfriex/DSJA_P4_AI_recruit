from __future__ import annotations

import pandas as pd


def corpus_status(units: pd.DataFrame) -> dict:
    hierarchy_columns = [
        column for column in ("majorName", "middleName", "minorName", "subName") if column in units
    ]
    hierarchy_present = (
        int(units[hierarchy_columns].notna().all(axis=1).sum()) if hierarchy_columns else 0
    )
    return {
        "status": "CANDIDATE",
        "unitRows": int(len(units)),
        "hierarchyNameCompleteRows": hierarchy_present,
        "dutyUnitBridgeRows": 0,
        "work24CrosswalkRows": 0,
        "promotionAllowed": False,
    }
