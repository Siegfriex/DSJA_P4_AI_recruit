from __future__ import annotations

import re
from collections import Counter

import pandas as pd

TOKEN = re.compile(r"[0-9A-Za-z가-힣]+")


def _tokens(value: str) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN.findall(str(value)))


def lexical_candidates(
    query: str, corpus: pd.DataFrame, text_column: str, top_k: int = 10
) -> pd.DataFrame:
    query_tokens = _tokens(query)
    if not query_tokens:
        return corpus.head(0).assign(score=pd.Series(dtype="float64"))
    result = corpus.copy()
    result["score"] = (
        result[text_column]
        .fillna("")
        .map(
            lambda value: (
                sum((query_tokens & _tokens(value)).values()) / max(sum(query_tokens.values()), 1)
            )
        )
    )
    return result.sort_values(["score", "ncsUnitCode"], ascending=[False, True]).head(top_k)
