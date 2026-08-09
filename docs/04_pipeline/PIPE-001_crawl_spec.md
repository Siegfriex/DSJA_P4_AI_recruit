# PIPE-001 — Linkareer Collection

## Input
month plan + approved query registry + source policy + approval artifact.

## Output
index discovery, raw posting versions, raw manifests, asset manifests, monthly coverage.

## Required behaviors
APQ request/variable validation, pagination, checkpoint/resume, distinct posting IDs,
detail frontier, terminal status, content-addressed raw recorder, retry/backoff,
rate/concurrency limits, kill switches.

## Fail closed
No network execution without valid approval scope, period, operation and request budget.

## Current state
Target spec FINAL; implementation PARTIAL.
