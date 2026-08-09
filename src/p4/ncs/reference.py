from __future__ import annotations

REFERENCE_AUTHORITIES = {"HUMAN_GOLD", "LLM_REFERENCE", "SILVER", "MODEL_PREDICTION"}


def validate_reference(authority: str, quality_evaluated: bool) -> None:
    if authority not in REFERENCE_AUTHORITIES:
        raise ValueError("UNKNOWN_REFERENCE_AUTHORITY")
    if authority == "LLM_REFERENCE" and quality_evaluated:
        raise ValueError("LLM_REFERENCE_CANNOT_IMPLY_EXTERNAL_TRUTH")
