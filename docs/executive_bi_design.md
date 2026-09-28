# Executive BI Design Contract

## Purpose

Phase 5 turns governed analytical metrics into a management decision surface.

The objective is not dashboard density. The objective is decision clarity.

## Current evidence boundary

Implemented in this branch:

- governed BI measure registry;
- DAX source expressions;
- explicit metric-to-BI mapping;
- page-level decision questions;
- audience ownership;
- visual-purpose contracts;
- blocking of deferred KPIs;
- CI validation that DAX and metric governance remain aligned.

Not yet claimed:

- a Power BI Desktop-opened PBIP artifact;
- PBIR visual rendering;
- cross-filter behavior validation;
- mobile layout;
- accessibility review;
- performance-analyzer results;
- screenshot-level executive UX approval.

Those items receive no BI implementation score until observable evidence exists.

## Page architecture

### Executive Command Center

Audience: GM / Owner / CFO.

Question: Where is operating pressure emerging, and which area deserves management attention first?

### Rooms & Revenue

Audience: GM / Revenue Manager.

Question: Is room-demand growth translating into healthy revenue productivity?

No occupancy denominator is joined to segment/channel facts at the wrong grain.

### F&B Leakage

Audience: F&B Director / Executive Chef / Controller.

Question: Is F&B topline improvement being diluted by purchasing, waste or discount pressure?

The page separates revenue context from direct leakage indicators.

### Labour & Operations

Audience: GM / Operations Director.

Question: Where is labour intensity increasing faster than operating demand?

Labour Cost % remains excluded because department-revenue allocation is not yet governed.

## Visual policy

Every visual must have a documented decision purpose.

Rejected patterns:

- decorative gauges without threshold governance;
- pie charts with excessive category count;
- mixed-grain measures on the same axis;
- red/green semantics without explicit directionality;
- hidden DAX measures outside the contract;
- executive cards for deferred metrics;
- causal wording from diagnostic association only.

## Source-control strategy

Power BI PBIP uses source-control friendly project structures. PBIR stores report definitions in JSON-based files and TMDL stores semantic-model metadata as text.

This repository will only claim a validated PBIP implementation after the project can be opened successfully in Power BI Desktop and the report/semantic-model files are committed as generated or validated artifacts.
