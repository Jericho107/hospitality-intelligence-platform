# Executive BI Architecture

## Status

Phase 5 introduces a source-control-first Power BI layer.

Implemented:

- TMDL semantic model;
- governed DAX measures;
- PBIR report structure;
- four executive page contracts;
- CI validation of measure coverage and report references;
- reverse test for a forbidden/deferred metric reference.

Not yet proven:

- Power BI Desktop open/save runtime validation;
- rendered visual containers;
- interaction behavior inside Power BI Desktop or Service;
- accessibility and pixel-level UX review on a rendered report.

The repository therefore does **not** yet claim a finished Power BI dashboard.

## Why TMDL + PBIR

The semantic model and report metadata are stored as text so Git can expose:

- measure changes;
- relationship changes;
- page changes;
- metric-reference drift;
- report-contract changes.

The BI layer is deliberately downstream of the PostgreSQL and KPI validation layers.

## Semantic-model rule

Ratios are recalculated from additive components in DAX.

Examples:

- Occupancy % = Rooms Sold / Rooms Available;
- ADR = Room Revenue / Rooms Sold;
- RevPAR = Room Revenue / Rooms Available;
- Waste % = Waste Qty / Depletion Qty;
- Overtime Share = Overtime Hours / Actual Hours.

The model does not SUM precomputed ratio columns.

## Deferred metrics

The following remain prohibited from the semantic model and report contract:

- Labour Cost %;
- Controllable Contribution;
- Contribution Margin %;
- Forecast Error.

They become eligible only after their upstream contracts are implemented and reverse-tested.

## Page contract

### Executive Overview

Decision question:

> Where is performance changing and which operating pressure requires management attention first?

Focus:

- Rooms;
- F&B topline;
- waste;
- purchasing variance;
- labour cost.

### Rooms Performance

Decision question:

> Is room revenue growth coming from demand, rate, or both?

### F&B and Inventory

Decision question:

> Are sales gains being diluted by discounting or recorded waste?

### Procurement and Labour

Decision question:

> Is controllable cost pressure coming from purchasing or labour intensity?

## Runtime boundary

PBIR and TMDL files are externally authored in this phase.

Passing repository CI proves internal contract consistency. It does not prove that a specific installed Power BI Desktop build can open, render and resave every externally authored artifact.

That runtime validation must be performed separately before the BI layer can receive full score.
