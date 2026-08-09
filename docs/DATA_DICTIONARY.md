# Data Dictionary

## Semantic additions

| Entity | Grain | Primary key | Required lineage |
|---|---|---|---|
| postingSourceBlock | source span | sourceBlockId | postingId, rawPostingId, rawSha256, parserVersion |
| sectionSourceBlock | section-block relation | sectionId + sourceBlockId | relationType |
| semanticChunk | atomic semantic span | chunkId | trackId, sectionId, sourceBlockId, chunkingVersion |

The complete legacy dictionary remains in `contracts/v2.1.2_legacy`. The
machine-readable 2.1.3 definitions are in
`contracts/v2.1.3_bridge/p4_contract.yaml`.
