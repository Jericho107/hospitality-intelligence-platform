<div align="center">

# Hospitality Intelligence Platform

### A multi-property decision system for hotel & F&B performance

**Business Intelligence · Hospitality Analytics · Data Engineering · Data Quality · Forecasting**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## The management question

> **Revenue is growing. Why is controllable operating contribution deteriorating — and where should management act first?**

This repository is being built as a synthetic end-to-end hospitality case study around that question.

The objective is not to produce another hotel dashboard. It is to connect the operational systems that actually drive performance — **PMS, POS, purchasing/inventory, workforce and budget** — into one governed analytical model capable of explaining **where value is created, where margin leaks and which action should be prioritised**.

**All data are synthetic. No hotel, restaurant, employer or client data are used.**

---

## Current implementation — Phase 1

Phase 1 establishes the operating-source and trust layer before any dashboard or management conclusion receives credit.

### Implemented now

- seeded synthetic multi-property operating sources;
- 13 explicit source files across PMS, POS, procurement, inventory, labour and budget;
- row-level Pydantic contracts;
- business-key uniqueness controls;
- PMS room-inventory reconciliation;
- POS outlet-check ↔ product-mix revenue reconciliation;
- purchasing ↔ inventory-receipt reconciliation;
- inventory roll-forward continuity;
- controlled `margin_leakage` scenario;
- pytest coverage for arithmetic contracts and scenario behavior;
- CI reverse test that deliberately corrupts POS product-mix revenue and requires validation to fail;
- clean-state regeneration and recovery validation.

### Not yet implemented

- PostgreSQL analytical target;
- dimensional marts;
- governed KPI materialisation;
- Power BI / DAX artifacts;
- diagnostic ranking of margin drivers;
- forecast models;
- quantified management-action impact.

Those items receive **zero scoring credit** until repository evidence exists.

---

## Business scope

The target portfolio contains three synthetic properties with different operating models:

| Property archetype | Core operating profile |
|---|---|
| **Urban Hotel** | rooms-led, corporate/transient mix, breakfast + restaurant + bar |
| **Leisure Resort** | high seasonality, rooms + multiple F&B outlets, stronger labour and purchasing exposure |
| **Boutique Hotel** | lower room inventory, premium ADR, lounge-led F&B |

The system is designed to answer management questions across:

- rooms revenue and demand;
- occupancy, ADR and RevPAR;
- channel and segment mix;
- F&B sales, discounts and product mix;
- purchasing and inventory consumption;
- waste and controllable cost leakage;
- labour scheduling, actual hours and overtime;
- budget versus actual;
- property, outlet and department contribution;
- forecast error and forward-looking demand.

---

## Source-system contract

| Source | File | Grain | Current control |
|---|---|---|---|
| Property master | `properties.csv` | property | unique property ID |
| Outlet master | `outlets.csv` | outlet | property FK |
| Product master | `products.csv` | product / outlet | outlet + property FK |
| Supplier master | `suppliers.csv` | supplier | unique supplier ID |
| Department master | `departments.csv` | department | unique department ID |
| PMS inventory | `pms_inventory_daily.csv` | property / day | available rooms > 0 |
| PMS bookings | `pms_bookings_daily.csv` | property / day / segment / channel | sold rooms ≤ inventory |
| POS checks | `pos_checks_daily.csv` | outlet / day | gross - discount = net |
| POS product mix | `pos_product_mix_daily.csv` | outlet / day / product | revenue reconciles to checks |
| Procurement | `purchases_daily.csv` | property / day / product / supplier | quantity × cost identity |
| Inventory | `inventory_daily.csv` | property / day / product | roll-forward + receipt reconciliation |
| Labour | `labour_daily.csv` | property / day / department | overtime bounded by actual hours |
| Budget | `budget_monthly.csv` | property / month / department | unique business key |

The source layer is intentionally validated **before** downstream analytics are allowed to trust it.

---

## Controlled business scenario

The generator currently supports:

- `healthy`
- `margin_leakage`

In `margin_leakage`, the synthetic leisure resort receives controlled pressure during the final 20 days:

- beverage purchase unit costs rise;
- beverage waste rises;
- F&B actual labour and overtime rise;
- demand strengthens slightly.

The construction creates a testable management tension: **topline activity can improve while controllable cost pressure deteriorates**.

This is an engineered synthetic scenario, not a discovered client result. Future diagnostics will only receive credit if they correctly identify the injected drivers and change when the scenario changes.

---

## Decision model

```text
PMS        POS        PROCUREMENT        WORKFORCE        BUDGET
 │          │              │                  │               │
 └──────────┴──────────────┴──────────────────┴───────────────┘
                            ↓
                     DATA CONTRACTS
                            ↓
                  VALIDATION & QUALITY
                            ↓
                     POSTGRESQL MODEL
                            ↓
                  GOVERNED KPI LAYER
                            ↓
           DIAGNOSTIC + PREDICTIVE ANALYTICS
                            ↓
                    EXECUTIVE BI LAYER
                            ↓
             PRIORITISED MANAGEMENT ACTIONS
                            ↓
                  MEASURED BUSINESS IMPACT
```

The first two layers are implemented. The remaining layers are target architecture until proven otherwise.

---

## Core business questions

1. Is revenue growth translating into better controllable contribution?
2. Which property, outlet or department explains the largest negative variance?
3. Is margin pressure driven by pricing, mix, purchasing, waste, discounting or labour?
4. Are higher occupancy periods creating profitable incremental F&B demand?
5. Which outlets or products create revenue but dilute contribution?
6. Where do actual labour hours systematically diverge from demand and schedule?
7. Which purchasing categories show adverse unit-cost or usage variance?
8. How much of performance variance is structural versus seasonal?
9. Where is forecast error concentrated?
10. Which management action has the highest measurable upside under documented assumptions?

---

## Governed KPI families

### Rooms
`Occupancy` · `ADR` · `RevPAR` · `Room Revenue` · `Channel Mix` · `Segment Mix`

### Food & Beverage
`Net F&B Revenue` · `Average Check` · `Cover Mix` · `Discount Rate` · `Product Mix` · `Outlet Contribution`

### Inventory & Purchasing
`Actual Product Cost` · `Waste Cost` · `Waste %` · `Purchase Price Variance` · `Usage Variance`

### Labour
`Scheduled Hours` · `Actual Hours` · `Overtime Hours` · `Labour Cost` · `Labour Cost %`

### Management
`Budget Variance` · `Controllable Contribution` · `Contribution Margin %` · `Forecast Error`

Every KPI requires a documented definition, grain, source, formula and limitation before it is treated as trusted.

`Controllable Contribution` is deliberately **not finalised** in Phase 1 because shared-cost scope and allocation policy are not yet governed.

---

## Technical target

| Layer | Implementation | Status |
|---|---|---|
| Synthetic operational sources | Python | **implemented** |
| Validation | Python + explicit contracts | **implemented** |
| Cross-source reconciliation | Python | **implemented at source layer** |
| Transformation | Python + SQL | planned |
| Analytical store | PostgreSQL | planned |
| Dimensional modelling | star-schema marts | planned |
| BI | Power BI / DAX | planned |
| Analytics | Python / statistical diagnostics | planned |
| Forecasting | baseline-first time-series / ML evaluation | planned |
| Software Quality | pytest + Ruff | **implemented** |
| Delivery | GitHub Actions | **implemented for Phase 1** |
| Documentation | contracts, assumptions, proof matrix | **implemented and evolving** |

---

## Target analytical model

```text
DIMENSIONS
├── dim_date
├── dim_property
├── dim_outlet
├── dim_room_segment
├── dim_channel
├── dim_product
├── dim_supplier
└── dim_department

FACTS
├── fact_rooms_daily
├── fact_pos_sales
├── fact_inventory_daily
├── fact_purchases
├── fact_labour_daily
└── fact_budget_monthly
```

This is a **target**, not current warehouse evidence. The final model must reconcile to its synthetic source systems before downstream KPIs are considered valid.

---

## Reverse test — Phase 1

The current CI proves a source-control failure path:

```text
seeded clean sources
        ↓
source contracts PASS
        ↓
mutate POS product-mix revenue only
        ↓
POS check ↔ product mix reconciliation FAILS
        ↓
regenerate the exact source state
        ↓
source contracts PASS
```

A happy-path generator without deliberate failure detection would not receive operational-proof credit.

Future phases must add reverse tests for the PostgreSQL target, metric contracts, management conclusions and forecasting.

---

## Local validation

```bash
python -m pip install -e ".[dev]"
make generate
make validate
pytest -q
ruff check .
```

Run the Phase 1 reverse test:

```bash
make reverse-test
```

---

## Proof standard

This flagship follows the Pretoria BI evidence rule:

> **No claim receives credit because it appears in a README. It receives credit only when the repository proves it.**

| Layer | Required proof |
|---|---|
| **Business Proof** | credible hospitality decision problem |
| **Analytical Proof** | conclusions supported by governed data and appropriate analysis |
| **Engineering Proof** | correct, testable and maintainable implementation |
| **Operational Proof** | reproducible pipeline, CI, failure handling and controls |
| **Value Proof** | quantified action logic with explicit assumptions and limitations |

See [`docs/proof_matrix.md`](docs/proof_matrix.md) for implemented versus unimplemented evidence.

---

## Repository architecture

```text
hospitality-intelligence-platform/
├── .github/workflows/ci.yml
├── docs/
├── src/hospitality_intelligence/
├── tests/
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
└── README.md
```

Empty folders are not created for presentation. A directory appears only when it contains real evidence.

---

## Officialisation rule

The repository is **not OFFICIAL**.

Current phase: **Phase 1 — source contracts and reverse-tested synthetic operating data**.

Officialisation requires:

- implementation of the end-to-end decision system;
- contradictory technical and commercial review;
- reverse tests across every material claim;
- no unsupported business-impact language;
- final score of **92/100 minimum**.

Internal flagship target: **95+/100 only if the evidence justifies it.**

---

<div align="center">

**Pretoria BI**

**Understand · Decide · Act · Measure**

</div>
