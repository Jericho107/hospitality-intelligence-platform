<div align="center">

# Hospitality Intelligence Platform

### A multi-property decision system for hotel & F&B performance

**Business Intelligence · Hospitality Analytics · Data Engineering · Data Quality · Forecasting**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## The management question

> **Revenue is growing. Why is controllable operating contribution deteriorating — and where should management act first?**

This repository implements a synthetic end-to-end hospitality decision system around that question.

The objective is not to produce another hotel dashboard. It is to connect the operational systems that actually drive performance — **PMS, POS, purchasing/inventory, workforce and budget** — into one governed analytical model capable of explaining **where value is created, where margin leaks and which action should be prioritised**.

**All data are synthetic. No hotel, restaurant, employer or client data are used.**

---

## Current implementation

The platform now enforces eight fail-closed evidence boundaries from synthetic source contracts through the governed BI, forecasting and value layers.

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
- paired healthy-versus-leakage diagnostic benchmark;
- ranked detection of injected beverage purchase-cost, beverage-waste and F&B overtime pressure;
- negative control proving the diagnostic engine does not report adverse drivers on healthy-versus-healthy data;
- source-controlled Power BI semantic model in TMDL;
- governed DAX measure layer mapped back to implemented KPI contracts;
- PBIR report/page scaffold for four management decision surfaces;
- 20 materialized PBIR visual containers generated deterministically from governed report and layout contracts;
- explicit visual-to-TMDL measure bindings, 1280×720 geometry and deterministic keyboard tab order;
- machine-readable report contract preventing unknown or deferred measures from entering BI;
- Microsoft PBIR conformance validation in CI via pinned `@microsoft/powerbi-report-authoring-cli@0.4.0`;
- Power BI Desktop Bridge evidence harness with pinned `@microsoft/powerbi-desktop-bridge-cli@1.0.0`;
- screenshot hash/fingerprint validator that rejects stale, incomplete or tampered Desktop evidence;
- governed seven-day-ahead room-demand forecasting protocol;
- seasonal-naive 7-day baseline versus HistGradientBoosting candidate;
- chronological train / validation / untouched final-test workflow;
- leakage guardrails requiring all target-derived features to be at least seven days old;
- multi-seed acceptance testing plus a deliberately weak zero-demand control;
- auditable 20-day management opportunity model for purchase price, waste and overtime premium;
- explicit conservative/base/stretch recovery assumptions at 25% / 50% / 75%;
- action owner, governed follow-up metric and 30-day review window for each value driver;
- healthy-control validation proving the value model reacts materially to controlled leakage;
- CI reverse tests and acceptance gates at eight levels:
  1. source contract corruption;
  2. raw PostgreSQL target mutation;
  3. analytical fact mutation;
  4. materialized KPI corruption;
  5. diagnostic truth / false-positive control;
  6. BI semantic/report-contract corruption;
  7. forecast candidate selection / rejection;
  8. management opportunity responsiveness / healthy control;
- deterministic recovery from each controlled failure.

### Not yet implemented

- **successful committed Power BI Desktop runtime evidence** from the Phase 9 harness;
- rendered screenshot evidence reviewed for executive UX;
- pixel-level decision UX and accessibility review in a rendered report;
- production-style diagnostic alert thresholds or causal attribution;
- production forecast validation on real booking-pace and exogenous demand data;
- observed post-action intervention impact and causal attribution.

Those items remain outside the implemented evidence boundary until repository evidence exists.
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

This is an engineered synthetic scenario, not a discovered client result. Future diagnostics are accepted only if they correctly identify the injected drivers and change when the scenario changes.

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

The source-contract, PostgreSQL, KPI-governance, synthetic diagnostic-validation, BI semantic-contract, PBIR visual-container, synthetic baseline-first forecasting, modeled management-opportunity and Desktop-runtime evidence-gate layers are implemented. Actual Power BI Desktop runtime evidence and realized intervention impact remain unproven until evidence is committed and validated.

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

## Governed BI measures

### Rooms
`Rooms Available` · `Rooms Sold` · `Room Revenue` · `Occupancy %` · `ADR` · `RevPAR`

### Food & Beverage
`Covers` · `F&B Gross Revenue` · `Discounts` · `Net F&B Revenue` · `Average Check` · `Discount Rate`

### Inventory & Purchasing
`Purchase Quantity` · `Actual Purchase Cost` · `Standard Purchase Cost` · `Purchase Price Variance` · `Usage Qty` · `Waste Qty` · `Waste Cost` · `Waste %`

### Labour
`Actual Hours` · `Overtime Hours` · `Labour Cost` · `Labour Cost per Hour` · `Overtime Share`

Ratios are recomputed in DAX from additive components; the BI layer does not SUM precomputed percentage/ratio columns.

Still deliberately excluded from BI until their upstream contracts are implemented: `Labour Cost %`, `Controllable Contribution`, `Contribution Margin %`, and `Forecast Error`.

---

## Forecasting evidence

The fixed room-demand protocol compares a seven-day seasonal-naive baseline with a HistGradientBoosting candidate at property-day grain.

On the primary synthetic seed, final-test WAPE moved from **6.00% to 3.76%**, a **37.29% relative improvement**, while MAE also decreased. Two additional seeds produced **36.91%** and **40.08%** final-test WAPE improvements, with no property-level WAPE regression observed in the guardrail. A zero-demand predictor was rejected before final-test evaluation.

These are synthetic benchmark results, not production hotel accuracy claims. See [docs/forecasting_results.md](docs/forecasting_results.md) and [docs/forecasting_validation.md](docs/forecasting_validation.md).

---

## Management opportunity evidence

The value layer converts three controlled operating pressures into explicit, reviewable management actions without claiming realized ROI.

For the synthetic leisure resort over the final 20-day leakage window, observed modeled exposure was:

- purchase-price pressure: **3,429.78**;
- excess waste: **1,584.99**;
- excess overtime premium: **1,798.33**.

Under the documented recovery assumptions, modeled recoverable opportunity is:

- conservative 25%: **1,703.28**;
- base 50%: **3,406.55**;
- stretch 75%: **5,109.83**.

The matched healthy control produces a base opportunity of **137.69**, so the leakage scenario is approximately **24.7×** higher under identical logic.

These are synthetic opportunity estimates, not realized savings or client ROI. Real impact remains unproven until an intervention is implemented and measured.

See [docs/management_action_value.md](docs/management_action_value.md) and [docs/management_value_results.md](docs/management_value_results.md).

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
| Diagnostic validation | paired scenario benchmark + negative control | **implemented** |
| BI semantic model | TMDL + governed DAX measures | **implemented** |
| BI report contract | PBIR page scaffold + machine-readable visual contract | **implemented** |
| PBIR visual layer | 20 deterministic visual containers + semantic bindings + layout checks | **implemented** |
| Microsoft PBIR conformance | official authoring CLI pinned in CI | **implemented** |
| Desktop runtime evidence gate | PBIP + Desktop Bridge harness + screenshot/fingerprint validation | **implemented; evidence pending** |
| BI runtime / decision UX | Power BI Desktop render/open/save + visual QA | not yet implemented |
| Analytics | diagnostic benchmark implemented; broader statistical analysis pending | **partial** |
| Forecasting | seasonal-naive baseline + HistGradientBoosting + chronological evaluation | **implemented on synthetic benchmark** |
| Management value model | explicit exposures + 25/50/75% recovery scenarios | **implemented on synthetic benchmark** |
| Realized impact attribution | observed intervention + post-action measurement | not yet implemented |
| Software Quality | pytest + Ruff | **implemented** |
| Delivery | Docker Compose + GitHub Actions | **implemented through Phase 9 CI** |
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

## Reverse tests — current validation stack

The current CI proves eight independent failure paths plus Microsoft PBIR conformance:

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

5. DIAGNOSTIC TRUTH CONTROL
healthy vs margin_leakage
→ recover purchase-cost + waste + overtime pressure
→ PASS
healthy vs healthy
→ zero adverse drivers
→ PASS

6. BI SEMANTIC / REPORT CONTRACT
clean TMDL + PBIR/report contract
→ BI validation PASS
→ inject deferred Controllable Contribution into a visual contract
→ BI validation FAIL
→ restore clean contract
→ PASS

7. FORECAST SELECTION
seasonal-naive baseline + candidate
→ candidate must win validation before final-test access
→ deliberately weak zero predictor
→ REJECTED

8. MANAGEMENT VALUE CONTROL
same logic on healthy + leakage scenarios
→ leakage opportunity must materially exceed healthy control
→ PASS

MICROSOFT PBIR CONFORMANCE
current .Report folder
→ official Microsoft authoring validator
→ PASS required
```

Warehouse validation does not rely only on global totals. KPI validation independently recalculates implemented metrics from facts and rejects drift in the materialized decision layer. Diagnostic validation includes a negative control, and BI validation fails closed when a deferred measure is introduced into the report contract.

Power BI Desktop runtime evidence and observed intervention-impact proof remain unproven.
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

Validate the Power BI semantic/report contracts:

```bash
make bi-validate
```

Validate committed Desktop runtime evidence:

```bash
make desktop-evidence-validate
```

Generate Desktop runtime evidence on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_powerbi_runtime_evidence.ps1 -InstallCli
```

---

## Validation standard

This project follows the Pretoria BI validation rule:

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
├── powerbi/
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

Current phase: **Phase 9 — Microsoft PBIR validation + reproducible Desktop evidence gate implemented; actual Desktop runtime capture still pending**.

Release readiness requires:

- implementation of the end-to-end decision system;
- contradictory technical and commercial review;
- reverse tests across every material claim;
- no unsupported business-impact language;
- all material claims to remain supported by executable repository evidence.

The implementation is considered mature only when the remaining runtime and intervention evidence is independently validated.

---

<div align="center">

**Pretoria BI**

**Understand · Decide · Act · Measure**

</div>
