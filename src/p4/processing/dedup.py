from __future__ import annotations

from difflib import SequenceMatcher

import pandas as pd


def _normalize(value: str) -> str:
    return " ".join(str(value or "").lower().split())


def assign_repost_groups(
    postings: pd.DataFrame, window_days: int = 90, threshold: float = 0.9
) -> pd.DataFrame:
    required = {"postingId", "companyKey", "titleText", "canonicalPostedAt", "postingEligibleFlag"}
    missing = required.difference(postings.columns)
    if missing:
        raise ValueError(f"postings missing dedup columns: {sorted(missing)}")
    result = postings.copy()
    result["canonicalPostedAt"] = pd.to_datetime(result["canonicalPostedAt"], utc=True)
    result = result.sort_values(
        ["companyKey", "canonicalPostedAt", "postingId"], na_position="last"
    )
    active: list[dict] = []
    assignment: dict[str, tuple[str, str, bool]] = {}
    for row in result.to_dict(orient="records"):
        posting_id = str(row["postingId"])
        if not row["postingEligibleFlag"] or pd.isna(row["canonicalPostedAt"]):
            assignment[posting_id] = (f"UNRESOLVED_{posting_id}", posting_id, True)
            continue
        match = None
        for group in reversed(active):
            if group["companyKey"] != row["companyKey"]:
                continue
            if (row["canonicalPostedAt"] - group["firstPostedAt"]).days > window_days:
                continue
            similarity = SequenceMatcher(
                None, _normalize(row["titleText"]), group["titleText"]
            ).ratio()
            if similarity >= threshold:
                match = group
                break
        if match is None:
            match = {
                "groupId": f"DUP_{posting_id}",
                "canonicalPostingId": posting_id,
                "companyKey": row["companyKey"],
                "firstPostedAt": row["canonicalPostedAt"],
                "titleText": _normalize(row["titleText"]),
            }
            active.append(match)
            canonical = True
        else:
            canonical = False
        assignment[posting_id] = (match["groupId"], match["canonicalPostingId"], canonical)
    result["duplicateGroupId"] = (
        result["postingId"].astype(str).map(lambda value: assignment[value][0])
    )
    result["canonicalPostingId"] = (
        result["postingId"].astype(str).map(lambda value: assignment[value][1])
    )
    result["canonicalRecordFlag"] = (
        result["postingId"].astype(str).map(lambda value: assignment[value][2])
    )
    result["dedupMode"] = (
        "PRODUCTION_90_DAY" if result["postingEligibleFlag"].any() else "OBSERVED_UNRESOLVED"
    )
    return result
