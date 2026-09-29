# PBIR Visual Containers

Phase 8 materializes the report contract into actual PBIR visual-container files.

## Evidence added

- 20 committed `visual.json` files;
- deterministic generation from `config/report_contract.yml` + `config/report_layout.yml`;
- explicit semantic bindings to governed TMDL measures;
- deterministic 1280×720 placement and keyboard tab order;
- CI comparison between regenerated files and committed PBIR;
- no deferred KPI is introduced.

## Visual mapping

- card → `cardVisual`;
- cards → `multiRowCard`;
- line → `lineChart`;
- clustered_bar → `clusteredBarChart`;
- matrix → `pivotTable`.

## Remaining boundary

The files use Microsoft's public PBIR visual-container schema and are structurally validated in Git. Power BI Desktop open/save/render validation is still a separate manual/runtime gate.

Therefore this phase proves **materialized PBIR report code**, not final rendered UX.
