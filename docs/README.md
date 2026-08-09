# P4 Data Product Design & SSOT Documentation Package

- Release: `P4-DPDD-SSOT-1.0.0`
- Version: `v1.0.0`
- Status: `FINAL_DESIGN_BASELINE`
- As-of: `2026-08-09`
- Code repository: `Siegfriex/DSJA_P4_AI_recruit`
- Local canonical workspace: `/home/sieg/projects-wsl/DSJA_P4_AI_recruit`
- Current implementation branch baseline: `migration/bootstrap@ac2ae67fdfd3898f999a2b4cdb6a2cdcf0f31acd`
- Main baseline: `main@e94913c8c105120b3b811b444dc759ddf3628c5f`

이 패키지는 P4의 **데이터 제품/분석 설계서(Data Product Design Document, DPDD)**와
**Project SSOT**, 데이터 계약·Data Card·파이프라인·전처리·모델·평가·리스크·기사 claim 규칙을
하나의 Frozen Reference 문서 체계로 통합한다.

`FINAL_DESIGN_BASELINE`은 문서 설계의 최종 기준선이라는 뜻이며, production 데이터·분석 결과가
완료되었다는 뜻이 아니다.

현재 실행 경계:

- `RAW_TO_SEMANTIC_REPLAY_READY = BLOCKED`
- `CANARY_PREFLIGHT_READY = BLOCKED`
- `PRODUCTION_DATA_READY = BLOCKED`
- `ANALYSIS_READY = BLOCKED`
- `ARTICLE_RESULT_READY = BLOCKED`

권위 구조:

1. `00_master/P4_DATA_PRODUCT_DESIGN_DOCUMENT.md`
2. `00_master/P4_PROJECT_SSOT.md`
3. `00_master/P4_RELEASE_MANIFEST.yaml`
4. 세부 `DATA-* / PIPE-* / EVAL-* / MODEL-* / RISK-*` 문서
5. 실제 run별 `EVD-*` immutable evidence

실데이터 raw/Parquet/DuckDB는 이 문서 패키지에 포함하지 않는다.
