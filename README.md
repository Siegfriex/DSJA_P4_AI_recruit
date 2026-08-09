# DSJA P4 AI Recruit

P4 DPDD/SSOT v1.0.0을 normative authority로 사용하는 clean canonical development base다.
실데이터는 로컬 전용이며 Git에는 synthetic fixture만 포함한다.

## 시작

```bash
cp .env.example .env
uv sync --all-groups --locked
uv run p4 contract validate
uv run p4 docs sync
uv run p4 docs check
uv run pytest -ra
```

## authority 경계

- `docs/00_master`, `01_research`~`07_article`, `09_governance`, `10_ops`: normative 문서
- `docs/08_evidence`, `manifests/runs`, `artifacts`: runtime evidence
- generated current-state 파일은 `p4 docs sync`만 갱신
- Linkareer/ATS/API collection은 서명된 approval 없이는 실행 불가
- fixture PASS는 observed/canary/production/analysis 승격을 뜻하지 않음

자세한 설계 authority는 [docs/README.md](docs/README.md)를 따른다.
