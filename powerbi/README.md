# Power BI Assets

This directory contains the source-controlled Executive BI layer.

## Current proof

- `HospitalityExecutive.SemanticModel/`: TMDL semantic model.
- `HospitalityExecutive.Report/`: PBIR report with 20 materialized visual containers.
- `config/bi_measure_contracts.yml`: canonical metric-to-DAX mapping.
- `config/report_contract.yml`: decision/page/visual specification.
- `python -m hospitality_intelligence.bi_contracts`: CI contract validation.

## Important limitation

The TMDL/PBIR assets are authored and structurally validated in Git, but **Power BI Desktop runtime open/save validation is not yet proven**.

The report visual containers are now committed and deterministically reproducible from `config/report_contract.yml` and `config/report_layout.yml`. They receive source-code/contract credit, but **not Desktop runtime or pixel-level UX credit** until the project is opened, rendered and reviewed in Power BI Desktop.

This separation prevents source-controlled PBIR code from being misrepresented as a fully runtime-validated dashboard.
