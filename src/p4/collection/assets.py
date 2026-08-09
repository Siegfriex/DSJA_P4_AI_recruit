from __future__ import annotations

from urllib.parse import urljoin

from .policy import is_allowed_linkareer_url


def hosted_asset_candidates(base_url: str, urls: list[str]) -> list[str]:
    candidates = []
    for value in urls:
        absolute = urljoin(base_url, value)
        if is_allowed_linkareer_url(absolute):
            candidates.append(absolute)
    return sorted(set(candidates))
