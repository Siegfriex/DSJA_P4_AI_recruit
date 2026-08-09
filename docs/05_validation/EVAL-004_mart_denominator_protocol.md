# EVAL-004 — Mart Denominator Audit

For each mart:
- grain uniqueness.
- numerator/denominator definition.
- canonical dedup application.
- unknown/abstain handling.
- month/job/sourceMode coverage.
- row-level reconciliation to upstream facts.
- main/sensitivity comparison.

RQ1 posting rates may not use track rows as posting denominator.
RQ2-B main and sensitivity must remain separate outputs.
