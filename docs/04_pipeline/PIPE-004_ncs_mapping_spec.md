# PIPE-004 — NCS Candidate / Mapping

DUTY chunk
→ candidate generation
→ ncs_candidate
→ ncs_candidate_source_score
→ fusion/rerank
→ reference
→ mapping terminal state
→ official NCS join.

## Candidate
Unique: candidateRunId × chunkId × ncsUnitCode.

## Candidate source scores
Separate rows for TOKEN_OVERLAP / TFIDF / BM25 / DENSE / EXACT_ALIAS /
WORK24_ALIAS / HIERARCHY_BACKOFF.

## Mapping
Every eligible DUTY chunk must have exactly one terminal mapping class.

## Main
SINGLE_ACCEPTED only.

## Sensitivity
MULTI_ACCEPTED included with 1/k at mart aggregation time.
