# RQ-002B — NCS Duty Mapping & Level

질문: 인턴 DUTY evidence가 어느 NCS 능력단위에 대응하며 공식 level/band 분포가 어떻게 관찰되는가?

## Grain
`eligible DUTY chunk × accepted NCS unit`

## Main mapping policy
- Main: SINGLE_ACCEPTED only.
- Sensitivity: SINGLE_ACCEPTED + MULTI_ACCEPTED with 1/k aggregation.
- Coverage denominator: all ncsEligible DUTY chunks.

## Level policy
NCS level은 텍스트에서 직접 예측하지 않는다.
accepted `ncsUnitCode`를 frozen NCS canonical corpus에 join하여 official level을 얻고 band로 결정론 변환한다.

## Mapping terminal states
SINGLE_ACCEPTED / MULTI_ACCEPTED / ABSTAIN / AMBIGUOUS /
OUT_OF_SCOPE / UNMAPPED / INSUFFICIENT_EVIDENCE.

## Publication
Mapping coverage와 terminal-state distribution이 반드시 band chart와 함께 제공되어야 한다.
