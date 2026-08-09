# MQ-001 — Source Recovery Quality

목적: HTML/ActivityText/OCR에서 생성한 source evidence가 semantic entities를 충분히 지지하는지 검증.

핵심 지표:
- detailTerminalCoverage
- rawFetchCoverage
- normalizationCoverage
- sectionEvidenceCoverage
- chunkPrimaryEvidenceCoverage
- OCR parse success / mapping eligibility

원칙:
- SourceBlock은 immutable evidence.
- Derived merged text는 별도 view.
- eligible semantic entity의 source lineage orphan은 0.
