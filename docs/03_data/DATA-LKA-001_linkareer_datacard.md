# DATA-LKA-001 — Linkareer Data Card

- Role: PRIMARY_CANONICAL
- Population denominator: YES
- Period: 2020-01~2026-07
- Collection: APQ index + detail SSR/Apollo + optional Linkareer-hosted assets
- Canonical source grain: posting retrieval version
- Raw storage: local-only, immutable/content-addressed
- Git tracked: NO raw empirical bytes

## Intended contents
sourcePostingId, sourceUrl, index metadata, SSR HTML, Activity/ActivityText,
hosted asset metadata/bytes, SHA-256, retrieval/run metadata.

## Inclusion
Confirmed recruitment posting in project source scope.

## Exclusion
External ATS transport, unbound/unauthorized source, non-recruitment content.

## Known limitations
Historical coverage and HTML/asset structure may vary by period.
Observed development data is not population authority.

## Quality
terminal state, raw SHA/bytes, source URL binding, period coverage,
parser recovery, sourceMode coverage.
