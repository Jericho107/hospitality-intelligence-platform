# Proof Matrix

This matrix distinguishes implemented evidence from planned architecture.

| Claim | Evidence | Reverse test | Status |
|---|---|---|---|
| Synthetic sources are reproducible | generator accepts seed + anchor | same configuration must produce byte-identical CSVs | implemented |
| Source files have explicit row contracts | Pydantic source models | invalid arithmetic identities are rejected | implemented |
| Business keys are unique | validator key definitions | duplicate keys cause validation failure | implemented |
| Room sales cannot exceed inventory | PMS cross-source validation | oversold source would fail validation | implemented |
| POS product mix reconciles to outlet checks | outlet-day revenue reconciliation | CI injects a product-mix mismatch and requires failure | implemented |
| Purchases reconcile to inventory receipts | product/day quantity reconciliation | mismatched receipts fail validation | implemented |
| Inventory roll-forward is continuous | prior closing vs next opening | broken continuity fails validation | implemented |
| Scenario contains controlled margin pressure | matched healthy/leakage test | same seed/anchor proves purchase, waste, labour and demand deltas | implemented |
| PostgreSQL raw landing matches source files | exact row count + canonical ordered SHA-256 | CI mutates raw POS revenue and requires reconciliation failure | implemented |
| Governed dimensional model exists | typed SQL dimensions and grain-specific facts | all fact counts and material totals reconcile to raw | implemented |
| Raw-to-analytics transformation detects drift | warehouse validator | CI mutates labour fact cost and requires validation failure | implemented |
| Power BI layer is decision-ready | dashboard artifacts + KPI evidence | metric/visual QA | not yet implemented |
| Forecasting improves on a baseline | modelling artifacts | naive baseline comparison | not yet implemented |
| Business actions have quantified impact | action model | assumptions + sensitivity | not yet implemented |

No score credit is given for rows marked `not yet implemented`.
