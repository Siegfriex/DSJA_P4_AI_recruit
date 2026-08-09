# Collection Policy

All network-capable CLI commands require an unexpired `--approval-file` bound
to the current source-policy and query-registry SHA-256 values. Only HTTPS
Linkareer hosts are allowed. External ATS transport is rejected before the
transport callable is invoked.

Canonical limits: one request per second, concurrency two, three retries with
exponential jitter, one consecutive 403, three consecutive 429 responses, and
minimum 80% success after five samples in a rolling window of twenty.

Migration network count is zero. GitHub publication traffic is repository
administration and is not a Linkareer/data-source call.

## Current implementation boundary

The policy client and approval hash checks exist, but collection orchestration
does not yet execute transport. `COLLECTION_IMPLEMENTATION_READY` therefore
remains `BLOCKED`. No approval file may be interpreted as permission beyond its
explicit scope, expiry, hashes, and remaining request budget.
