from __future__ import annotations

import pandas as pd
import pytest

from p4.ncs.reference import validate_reference
from p4.ncs.retrieval import lexical_candidates


def test_lexical_retrieval_is_deterministic() -> None:
    corpus = pd.DataFrame({"ncsUnitCode": ["B", "A"], "text": ["데이터 분석", "데이터 분석"]})
    result = lexical_candidates("데이터 분석", corpus, "text", top_k=2)
    assert result.ncsUnitCode.tolist() == ["A", "B"]


def test_llm_reference_does_not_claim_external_truth() -> None:
    with pytest.raises(ValueError, match="EXTERNAL_TRUTH"):
        validate_reference("LLM_REFERENCE", quality_evaluated=True)
