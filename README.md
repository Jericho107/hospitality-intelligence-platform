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

## Current implementation — Phase 3

The platform now proves two separate data-trust boundaries before KPI or dashboard logic receives credit.

### Implemented now

- seeded synthetic multi-property operating sources across PMS, POS, procurement, inventory, labour and budget;
- explicit row, domain, ownership and cross-source contracts;
- PostgreSQL 16 raw landing schema preserving source values as text;
- exact CSV → raw PostgreSQL reconciliation using ordered row counts + SHA-256;
- typed dimensional analytical schema with surrogate keys, PK/FK constraints and grain-specific facts;
- separate room inventory and room bookings facts to protect denominator grain;
- reconciliation of **all fact row counts**;
- reconciliation of material operational quantities and financial totals;
- business-key lineage checks from raw rows back through analytical dimensions and facts;
- dimension lineage controls for property, outlet, product, supplier, department, date, segment and channel;
- machine-readable KPI contracts with explicit grain, formula, owner, exclusions, reconciliation and limitations;
- materialized KPI marts for Rooms, F&B, Purchasing, Inventory and Labour;
- independent KPI reconciliation back to analytical facts;
- CI reverse tests at four levels:
  1. source contract corruption;
  2. raw PostgreSQL target mutation;
  3. analytical fact mutation;
  4. materialized KPI corruption;
- deterministic recovery from each controlled failure.

### Not yet implemented

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

The source-contract, validation and PostgreSQL modelling layers are implemented. KPI, diagnostic, BI and business-impact layers remain target architecture until proven otherwise.

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

`Controllable Contribution` is deliberately **not finalised** in Phase 2 because shared-cost scope and allocation policy are not yet governed.

---

## Technical implementation

| Layer | Implementation | Status |
|---|---|---|
| Synthetic operational sources | Python | **implemented** |
| Source validation | Pydantic + cross-source contracts | **implemented** |
| Raw landing | PostgreSQL 16 | **implemented** |
| Source → raw reconciliation | row count + canonical SHA-256 | **implemented** |
| Transformation | SQL + Python orchestration | **implemented** |
| Dimensional modelling | typed grain-specific facts + dimensions | **implemented** |
| Raw → analytics validation | counts + quantities + financial + lineage controls | **implemented** |
| KPI governance | machine-readable contracts | **implemented** |
| KPI materialisation | SQL marts + independent reconciliation | **implemented** |
| BI | Power BI / DAX | not yet implemented |
| Analytics | Python / statistical diagnostics | not yet implemented |
| Forecasting | baseline-first time-series / ML evaluation | not yet implemented |
| Software Quality | pytest + Ruff | **implemented** |
| Delivery | Docker Compose + GitHub Actions | **implemented through Phase 2** |
| Documentation | architecture, model, contracts, assumptions, proof matrix | **implemented and evolving** |
---

## Current analytical model

```text
DIMENSIONS
├── dim_date
├── dim_property
├── dim_outlet
├── dim_product
├── dim_supplier
├── dim_department
├── dim_room_segment
└── dim_channel

FACTS
├── fact_room_inventory_daily
├── fact_room_bookings_daily
├── fact_pos_outlet_daily
├── fact_pos_product_daily
├── fact_purchases_daily
├── fact_inventory_daily
├── fact_labour_daily
└── fact_budget_monthly
```

Facts remain separated at their natural grains. In particular, room inventory is **property × day**, while booked rooms are **property × day × segment × channel**. Combining them would duplicate inventory denominators and make occupancy unsafe.

See [`docs/data_model.md`](docs/data_model.md) for the grain contract.
---

## Reverse tests — Phase 2

The current CI must prove three independent failure paths:

```text
1. SOURCE CONTRACT
clean source
→ mutate POS product-mix revenue
→ source validation FAIL
→ regenerate
→ PASS

2. SOURCE → RAW POSTGRESQL
source CSV unchanged
→ mutate raw PostgreSQL POS revenue
→ exact row/hash reconciliation FAIL
→ reload raw
→ PASS

3. RAW → ANALYTICS
clean raw + clean dimensional build
→ mutate analytical labour cost only
→ warehouse validation FAIL
→ rebuild analytics
→ PASS

4. GOVERNED KPI LAYER
clean analytical facts
→ build KPI marts
→ metric validation PASS
→ mutate materialized ADR only
→ metric validation FAIL
→ rebuild KPI marts
→ PASS
```

Warehouse validation does not rely only on global totals. KPI validation independently recalculates implemented metrics from facts and rejects drift in the materialized decision layer.

Future phases must add reverse tests for management conclusions, Power BI behavior and forecasting.
---

## Local validation

```bash
python -m pip install -e ".[dev]"
make generate
make validate
pytest -q
ruff check .
```

Run the complete PostgreSQL pipeline:

```bash
make pipeline
```

Run the source-contract reverse test:

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
├── sql/
├── src/hospitality_intelligence/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```

Empty folders are not created for presentation. A directory appears only when it contains real evidence.

---

## Officialisation rule

The repository is **not OFFICIAL**.

Current phase: **Phase 3 — governed and reverse-tested KPI layer**.

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
