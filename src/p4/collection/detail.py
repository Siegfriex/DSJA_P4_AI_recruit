from __future__ import annotations

import json
import re
from typing import Any

NEXT_DATA = re.compile(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL)


def parse_next_data(html: str) -> dict[str, Any]:
    match = NEXT_DATA.search(html)
    if not match:
        raise ValueError("NEXT_DATA_NOT_FOUND")
    return json.loads(match.group(1))


def select_activity_text(apollo_state: dict[str, Any], source_posting_id: str) -> dict[str, Any]:
    exact = apollo_state.get(f"ActivityText:{source_posting_id}")
    if isinstance(exact, dict):
        return exact
    candidates = [
        value
        for key, value in apollo_state.items()
        if key.startswith("ActivityText:") and isinstance(value, dict)
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("ACTIVITY_TEXT_AMBIGUOUS_OR_MISSING")
