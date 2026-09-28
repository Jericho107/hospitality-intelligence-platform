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
| Scenario contains controlled margin pressure | generator + matched healthy/leakage scenario test | same seed/anchor must show the documented purchase, waste, labour and demand deltas | implemented |
| PostgreSQL analytical target is reconciled | target architecture | source-to-target reconciliation | not yet implemented |
| Governed star schema exists | SQL marts | grain + FK + reconciliation tests | not yet implemented |
| Power BI layer is decision-ready | dashboard artifacts + KPI evidence | metric/visual QA | not yet implemented |
| Forecasting improves on a baseline | modelling artifacts | naive baseline comparison | not yet implemented |
| Business actions have quantified impact | action model | assumptions + sensitivity | not yet implemented |

No score credit is given for rows marked `not yet implemented`.
