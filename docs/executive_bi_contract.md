# Executive BI Contract

## Why Phase 5 starts with a contract

The report layer is allowed to consume governed analytical metrics, not redefine them.

This prevents a common BI failure mode:

1. SQL computes one KPI;
2. DAX silently computes another;
3. the dashboard looks correct;
4. nobody can explain why the numbers differ.

## Current BI scope

The semantic contract includes only the 11 metrics currently marked `implemented` in `config/metric_contracts.yml`.

Deferred metrics are deliberately excluded:

- Labour Cost %
- Controllable Contribution

They will not appear in the executive layer until their denominator/cost-scope governance exists.

## Decision pages

### Executive Overview

Question: where is operating performance changing, and which pressure deserves management attention first?

### Rooms Performance

Question: is room revenue growth coming from demand, rate, or both?

### F&B Margin Drivers

Question: which controllable F&B pressures are rising despite topline activity?

### Labour & Purchasing

Question: where are labour intensity and purchasing variance creating avoidable pressure?

## Current evidence boundary

Phase 5 currently proves the semantic/report contract and canonical DAX definitions.

It does **not** yet claim:

- a Desktop-openable PBIP package;
- a rendered Power BI report;
- visual QA inside Power BI Desktop;
- deployment to Fabric;
- production RLS.

Those require separate evidence before BI receives full scoring credit.
