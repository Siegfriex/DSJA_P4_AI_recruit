# Canonical Entity Registry

| Entity | Layer | Grain | Key |
|---|---|---|---|
| raw_posting_version | SOURCE_EVIDENCE | posting retrieval version | rawPostingId |
| posting_source_block | SOURCE_EVIDENCE | source span | sourceBlockId |
| derived_text_view | DERIVED | derived section/chunk text | derivedTextId |
| posting_normalized | CANONICAL_ENTITY | posting | postingId |
| posting_track | CANONICAL_ENTITY | recruitment track | trackId |
| posting_section | CANONICAL_ENTITY | semantic section | sectionId |
| section_source_block | BRIDGE | section×block | sectionId+sourceBlockId |
| semantic_chunk | CANONICAL_ENTITY | atomic semantic span | chunkId |
| chunk_source_block | BRIDGE | chunk×block | chunkId+sourceBlockId |
| requirement_mention | ATOMIC_MENTION | raw requirement expression | mentionId |
| requirement_fact | LOGICAL_FACT | normalized requirement | requirementFactId |
| requirement_fact_mention | BRIDGE | fact×mention | composite |
| skill_requirement_fact | LOGICAL_FACT | normalized skill condition | skillFactId |
| intern_pathway_fact | LOGICAL_FACT | intern track pathway | trackId |
| selection_process_stage_fact | LOGICAL_FACT | explicit stage | selectionStageId |
| duty_action_mention | ATOMIC_MENTION | duty action expression | dutyActionMentionId |
| track_requirement_summary | DERIVED_SUMMARY | track | trackId |
| track_duty_action_summary | DERIVED_SUMMARY | track | trackId |
| posting_dedup_membership | CANONICALIZATION | posting | postingId |
| ncs_candidate | REFERENCE_RETRIEVAL | run×chunk×unit | candidateId |
| ncs_candidate_source_score | REFERENCE_RETRIEVAL | candidate×source | composite |
| ncs_mapping_reference | REFERENCE_MAPPING | mapping | mappingId |
| rq1_posting_monthly_global_mart | MART | month | periodMonth |
| rq1_track_monthly_job_mart | MART | month×job×trackType | composite |
| rq2a_track_fact | MART_FACT | track | trackId |
| rq2a_monthly_mart | MART | month×job×trackType | composite |
| ncs_mapping_coverage_mart | MART | month×job×sourceMode | composite |
| ncs_band_distribution_main_mart | MART | month×job×band | composite |
| ncs_band_distribution_sensitivity_mart | MART | month×job×band | composite |
| article_claim | PUBLICATION | claim | claimId |
| article_claim_evidence | PUBLICATION | claim×evidence | composite |
