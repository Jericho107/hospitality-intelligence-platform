# Power BI Assets

This directory contains the source-controlled Executive BI layer.

## Current proof

- `HospitalityExecutive.SemanticModel/`: TMDL semantic model.
- `HospitalityExecutive.Report/`: PBIR report scaffold.
- `config/bi_measure_contracts.yml`: canonical metric-to-DAX mapping.
- `config/report_contract.yml`: decision/page/visual specification.
- `python -m hospitality_intelligence.bi_contracts`: CI contract validation.

## Important limitation

The TMDL/PBIR assets are authored and structurally validated in Git, but **Power BI Desktop runtime open/save validation is not yet proven**.

The report pages intentionally contain no committed visual containers yet. Visuals will receive score only after the PBIR definitions are materialized and runtime-validated.

This separation prevents a report specification from being misrepresented as a finished dashboard.
