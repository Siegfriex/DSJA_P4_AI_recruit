# PIPE-003 — Mention / Fact / Extension Semantics

## Requirement
requirement_mention → requirement_fact → track_requirement_summary.

## Extension facts
- skill_requirement_fact
- intern_pathway_fact
- selection_process_stage_fact
- duty_action_mention
- track_duty_action_summary

## Dedup
Detailed writing must not inflate barrier counts.
Summary distinct key defaults to track×normalized subject×obligation.

## Selection
`explicitSelectionStageCount`; NOT_STATED is not zero.

## Duty
workStage is nominal; responsibilityLevel is separate ordinal dimension.
