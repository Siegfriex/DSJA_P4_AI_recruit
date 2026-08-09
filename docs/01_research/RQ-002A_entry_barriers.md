# RQ-002A — Entry Barriers & Requirements

질문: 신입·인턴의 명시적 진입요건과 요구조건은 시점·직무별로 어떻게 관찰되는가?

## Grain
`track × normalized logical requirement`

## Core labels
- Career: E0/E1/E2/E3/U
- Intern access: I0/I1/IU
- Intern pathway: EXPERIENTIAL / CONVERSION_LINKED / PROJECT_BASED / UNKNOWN

## Atomic architecture
`requirement_mention → requirement_fact → skill_requirement_fact → track_requirement_summary`

## Main features
- minCareerMonths
- portfolio/project/certificate/degree
- required/preferred skill distinct counts
- skill action levels
- explicitly disclosed selection stages

`NOT_STATED`를 0으로 대체하지 않는다.
UNKNOWN/conflict/resolution rate를 함께 보고한다.
