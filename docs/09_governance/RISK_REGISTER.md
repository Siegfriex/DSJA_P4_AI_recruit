# Risk Register

| ID | Risk | Severity | Control |
|---|---|---|---|
| RISK-001 | Historical source coverage bias | P1 | month coverage and exclusion/shading |
| RISK-002 | Unauthorized/unstable collection | P1 | source policy + approval binding + kill switch |
| RISK-003 | Raw→semantic lineage gap | P1 | E2E replay and evidence bridges |
| RISK-004 | Detailed JD overcount | P1 | mention/fact/summary separation |
| RISK-005 | Job taxonomy time drift/leakage | P1 | frozen taxonomy + drift queue |
| RISK-006 | Company over-merge | P2 | legalEntityKey/parentCompanyKey split |
| RISK-007 | OCR time/job bias | P1 | sourceMode coverage mart |
| RISK-008 | NCS mapping uncertainty | P1 | terminal states, abstain, external quality eval |
| RISK-009 | Multi-label band distortion | P1 | main single / sensitivity 1/k |
| RISK-010 | Causal overclaim | P1 | article claim protocol |
| RISK-011 | Secret/raw data exposure | P0 | Git ignore, secret scan, local-only raw |
| RISK-012 | Stale spec/evidence authority | P2 | frozen release manifest and SHA |
