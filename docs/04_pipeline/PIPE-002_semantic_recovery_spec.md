# PIPE-002 — Raw-to-Semantic Recovery

## Stage order
raw posting → posting normalization → SourceBlock → track → section + bridge
→ semantic chunk + bridge.

## Important
SourceBlock is created before section because it is raw evidence.
Section is interpreted inside track boundary.
Chunk must have primary source evidence.

## Output
posting_normalized, posting_source_block, posting_track, posting_section,
section_source_block, semantic_chunk, chunk_source_block.

## Acceptance
raw29 local E2E must be reproducible using new code only before production promotion.
