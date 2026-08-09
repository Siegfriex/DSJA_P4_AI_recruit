# Metric Registry

| ID | Metric | Grain | Numerator | Denominator | Unknown rule |
|---|---|---|---|---|---|
| METRIC-RQ1-ENTRY | entryPostingRate | month | postings with entry | distinct eligible canonical postings | unresolved excluded + separately reported |
| METRIC-RQ1-INTERN | internPostingRate | month | postings with intern | distinct eligible canonical postings | same |
| METRIC-RQ2A-I1 | restrictedInternShare | month×job | eligible I1 intern tracks | known eligible intern tracks | IU separately |
| METRIC-RQ2A-PATH | conversionLinkedShare | month×job | conversion-linked intern tracks | pathway-resolved intern tracks | resolution rate required |
| METRIC-RQ2A-STAGE | explicitSelectionStageCount | track | explicit stages | not a rate | NOT_STATED ≠ 0 |
| METRIC-NCS-COV | singleMappingCoverage | month×job | SINGLE_ACCEPTED eligible DUTY chunks | all eligible DUTY chunks | all terminal states shown |
| METRIC-NCS-BAND | mainBandShare | month×job×band | single accepted chunks in band | SINGLE_ACCEPTED chunks | coverage reported separately |
| METRIC-NCS-SENS | sensitivityBandShare | month×job×band | weighted accepted units | total accepted chunk weight | multi 1/k |
