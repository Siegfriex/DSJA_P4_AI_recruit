# Taxonomy Registry

Frozen taxonomies:
- job family
- career access
- intern access
- intern pathway
- selection process
- skill family
- skill action level
- work stage
- responsibility level
- NCS band

## Version fields
Every taxonomy release records:
`taxonomyVersion`, `taxonomyName`, `taxonomySha256`, `parentVersion`,
`developedUsingPeriodEnd`, `effectiveFrom`, `status`, `changeSummary`.

## Leakage rule
Frozen-audit data may not be used to modify a taxonomy applied to that same audit.
New concepts become `UNKNOWN` or `DRIFT_CANDIDATE`.

## Skill action level
UNKNOWN, AWARENESS, USE, IMPLEMENT, OPERATE, DESIGN.
Ordinal only; numeric encoding is not interval-scale.

## Responsibility level
UNKNOWN, SUPPORT, EXECUTE, INDEPENDENT, OWN_DESIGN, LEAD.

## Work stage
Nominal:
RESEARCH_DOCUMENTATION, ROUTINE_OPERATION, DATA_LABELING, TEST_QA_DEBUG,
IMPLEMENTATION, MODEL_TRAINING, DEPLOYMENT_MAINTENANCE, SYSTEM_DESIGN,
DOMAIN_COLLABORATION, UNKNOWN.
