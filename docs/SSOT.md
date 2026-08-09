# P4 Single Source of Truth

## Scope

P4 studies Linkareer recruitment postings from 2020-01 through 2026-07 for a
reviewed AI·IT cohort. RQ1 measures entry/intern/experienced posting structure;
RQ2-A measures entry barriers and requirements; RQ2-B maps intern duty evidence
to NCS units, levels, and bands.

Korea-wide labor-market, Work24, and AI-exposure causal designs are not part of
the primary scope. They may be retained only under `docs/extensions/`.

## Authority order

1. immutable raw bytes and SHA-256
2. current data/release manifest
3. Contract 2.1.3 bridge and tracked source
4. current run artifact
5. tests and validators
6. audit report
7. planning documents

Code existence is not execution. Fixture, observed, canary, production,
quality-evaluated, canonical-promoted, analysis-ready, and article-ready states
are always reported separately.

## Current migration boundary

The observed 137-row bundle is a regression target only. It is not a population
denominator. `empiricalAnalysisAllowed=false`, `promotionAllowed=false`, and
`highDemandScore=NULL` remain mandatory. A `resultManifest` cannot be created
until production release, semantic, NCS quality, and analysis gates pass.
