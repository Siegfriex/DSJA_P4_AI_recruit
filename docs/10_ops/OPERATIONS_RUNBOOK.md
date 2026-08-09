# P4 Operations Runbook

## Environment
Python 3.12 + uv.lock.

## Before every run
1. resolve code commit.
2. validate contract/taxonomy versions.
3. validate source-policy/approval if network-capable.
4. create unique runId and immutable output directory.
5. record input manifests.

## After every run
1. schema/PK/FK checks.
2. row/coverage summary.
3. content/output SHA.
4. test log SHA.
5. evidence attestation.
6. gate evaluation.

## Failure
No partial artifact is promoted.
Retry requires a new or explicitly resumable run state.
Never overwrite an immutable accepted run.

## Drift
Source/API, taxonomy, data distribution and NCS corpus changes trigger review before promotion.
