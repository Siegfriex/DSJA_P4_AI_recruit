from __future__ import annotations


def empty_evaluation() -> dict:
    return {
        "status": "NOT_EVALUATED",
        "goldRows": 0,
        "precision": None,
        "recall": None,
        "f1": None,
        "coverage": None,
        "promotionAllowed": False,
    }
