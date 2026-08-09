# Statistical Analysis Plan

## RQ1
Monthly rates and composition; graphical trend; 2023 observational breakpoint;
segmented regression with HAC where assumptions are satisfied.

## RQ2-A
Monthly/cohort requirement shares, career/access class distributions,
median minCareerMonths, skill/selection/pathway metrics.

## RQ2-B
Mapping coverage first; main single-mapping band distribution;
weighted multi-label sensitivity; work-stage/NCS cross-tab.

## Models
Potential segmented form:
outcome_t = β0 + β1*time + β2*post2023 + β3*timeAfter2023 + controls + error.

This is an association model, not causal identification.

## Sensitivities
- breakpoint 2022Q4 / 2023Q1 / 2023Q2 / 2024Q1.
- pre/post dedup.
- primary-job resolved subset.
- NCS main vs multi-label sensitivity.
- sourceMode/OCR coverage.
- 2026 YTD comparable window.
