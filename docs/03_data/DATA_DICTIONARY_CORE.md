# Core Data Dictionary — Summary

## Identifiers
- postingId: normalized posting.
- rawPostingId: immutable raw retrieval version.
- trackId: recruitment track.
- sectionId: semantic section.
- sourceBlockId: immutable source evidence span.
- chunkId: atomic semantic span.
- mentionId: raw observed expression.
- requirementFactId: normalized logical condition.
- candidateId: candidateRun×chunk×NCS unit.
- mappingId: mapping reference.

## Eligibility
- postingEligibleFlag
- rq1EligibleFlag
- rq2EligibleFlag
- ncsEligibleFlag

All are fail-closed boolean fields with explicit reason/status fields.

## Missingness
Unknown, not stated, conflicting and unavailable are not silently converted to false/zero.

## Machine canonical
DuckDB/Parquet.

## Inspection export
CSV.

## Reserved
`highDemandScore=NULL`.
