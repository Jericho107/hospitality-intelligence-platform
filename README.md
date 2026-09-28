<div align="center">

# Hospitality Intelligence Platform

### A decision system for hospitality margin, operations and performance

**Pretoria BI — flagship case study**

`Hospitality Analytics` · `Business Intelligence` · `Data Engineering` · `Forecasting` · `Data Quality`

</div>

---

## The management problem

Revenue can grow while operating margin deteriorates.

In hospitality, that deterioration can come from several mechanisms at once:

- occupancy gained through expensive channels;
- ADR growth offset by distribution cost;
- F&B revenue growth with worsening food or beverage cost;
- labour hours increasing faster than demand;
- purchase prices drifting above standard;
- theoretical and actual inventory consumption diverging;
- menu mix moving toward low-contribution items;
- forecasts missing demand peaks and driving poor operating plans.

The question is therefore not simply:

> **What happened?**

It is:

> **Where is margin being created or destroyed, why is it happening, what action should management take next, and how will we measure whether that action worked?**

This repository is being built around that decision.

---

## Executive decision scope

The platform must support six management decisions:

| Decision | Management question |
|---|---|
| Revenue | Where is commercial performance strengthening or weakening? |
| Margin | Which properties, outlets, channels or products create or destroy contribution? |
| Purchasing | Is cost deterioration driven by supplier price, volume or mix? |
| Labour | Is staffing aligned with demand and revenue? |
| Inventory & waste | Where is operational leakage emerging? |
| Forecasting | What demand should management plan for, and with what uncertainty? |

The technology is subordinate to those decisions.

---

## Target operating model

```text
PMS · POS · PURCHASING · INVENTORY · LABOUR · BUDGET
                        │
                        ▼
                SOURCE CONTRACTS
                        │
                        ▼
              VALIDATION + QUALITY
                        │
                        ▼
                PYTHON PIPELINE
                        │
                        ▼
             POSTGRESQL WAREHOUSE
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        SQL / METRICS         ANALYTICS
             │                     │
             └──────────┬──────────┘
                        ▼
                  POWER BI
                        │
                        ▼
              MANAGEMENT ACTION
                        │
                        ▼
                MEASURED IMPACT
```

Every arrow above must eventually have executable evidence. Until then it remains a target, not a claim.

---

## Analytical perimeter

### Rooms

Occupancy · ADR · RevPAR · Net RevPAR · channel economics · room-revenue variance

### Food & Beverage

Net sales · food cost · beverage cost · gross margin · contribution · product mix · outlet performance

### Purchasing & inventory

Purchase price variance · supplier variance · theoretical consumption · actual consumption · inventory variance · waste

### Labour

Paid hours · labour cost · labour cost % · revenue per labour hour · demand alignment

### Planning

Budget variance · demand forecast · forecast error · operational planning signals

---

## Metric governance

Metrics are defined in machine-readable contracts under:

```text
config/metric_contracts.yml
```

A metric is rejected if it does not define:

- business purpose;
- exact formula;
- grain;
- source datasets;
- owner;
- refresh expectation;
- exclusions;
- reconciliation rule;
- known limitations.

The contracts are validated in CI.

See [Metric Contracts](docs/metric_contracts.md).

---

## Source governance

Synthetic operational systems are specified before generation:

```text
config/source_contracts.yml
```

Each source declares:

- business system;
- grain;
- primary key;
- required fields;
- key relationships;
- time field;
- financial fields where relevant;
- explicit PII boundary.

No source generator is allowed to invent a schema independently of these contracts.

---

## Dimensional model target

### Facts

```text
fact_room_nights
fact_fnb_sales
fact_purchases
fact_inventory_movements
fact_labour
fact_budget
```

### Dimensions

```text
dim_date
dim_property
dim_outlet
dim_product
dim_supplier
dim_employee_role
dim_channel
```

The model is intentionally dimensional because the primary consumer is a management decision layer, not an application transaction store.

See [Data Model](docs/data_model.md).

---

## Evidence model

The flagship will not be judged by screenshots alone.

| Evidence layer | Acceptance question |
|---|---|
| Business proof | Does the analysis change a meaningful management decision? |
| Analytical proof | Do the data and method support the conclusion? |
| Engineering proof | Are transformations and controls inspectable and tested? |
| Operational proof | Can the workflow fail safely and be reproduced? |
| Value proof | Can the action be measured against a baseline? |

---

## Reverse-test policy

The final system must survive deliberately adverse scenarios, including:

- duplicate POS lines;
- missing PMS dates;
- orphan product or supplier keys;
- impossible negative room inventory;
- purchase-price spikes;
- inventory leakage;
- labour hours inconsistent with operating state;
- KPI numerator/denominator corruption;
- source-to-target row loss;
- dashboard/warehouse metric mismatch;
- forecast that fails to beat a simple baseline.

A control is not considered credible until we can show what happens when the controlled condition is broken.

---

## Current implementation status

### Implemented

- business problem and management decisions;
- machine-readable source contracts;
- machine-readable metric contracts;
- contract-validation Python package;
- tests for governance rules;
- dimensional-model target;
- architecture and validation strategy;
- strict scoring rubric.

### Not yet claimed

- generated operational datasets;
- ETL/ELT completion;
- PostgreSQL warehouse implementation;
- Power BI dashboard;
- forecast performance;
- quantified business impact;
- production readiness.

**Status: FOUNDATION — NOT OFFICIAL**

---

## Quality gate

This repository is not officialised because it looks polished.

It must earn the score.

The scoring rubric is intentionally punitive. Critical failures can cap the total score regardless of cosmetic quality.

See [Scoring Rubric](docs/scoring_rubric.md).

---

## Local contract validation

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
python -m hospitality_intelligence.contracts
```

---

## Pretoria BI

This flagship combines hospitality-domain reasoning with Data/BI engineering.

The intended outcome is not a prettier dashboard.

It is a trusted decision system that explains **where performance changed, why it changed, what action is justified, and whether that action improved the result**.

[pretoriabi.com](https://pretoriabi.com)
