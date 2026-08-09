# RQ-001 — Posting Structure

질문: Linkareer AI·IT 유효공고에서 신입·인턴·경력·혼합 모집구조가 월별로 어떻게 관찰되는가?

## Main grain
`canonicalPostingId × periodMonth`

## Main denominator
`COUNT(DISTINCT canonicalPostingId)` where:
- `postingEligibleFlag=true`
- `rq1EligibleFlag=true`
- `canonicalRecordFlag=true`

## Main mart
`rq1_posting_monthly_global_mart`

## Job analysis
직무별 main은 track grain으로 분리한다.
`rq1_track_monthly_job_mart`를 공고 수로 부르지 않는다.

## Required coverage
- recruitment type resolution.
- primary source/date authority.
- dedup coverage.
- month coverage.
- unknown rate.

## Sensitivity
- pre-dedup.
- alternative breakpoint.
- primary-job-resolved subset.
