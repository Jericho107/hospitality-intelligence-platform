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

---

## Technical target

| Layer | Implementation |
|---|---|
| Synthetic operational sources | Python |
| Validation | Python + explicit data contracts |
| Transformation | Python + SQL |
| Analytical store | PostgreSQL |
| Dimensional modelling | star-schema marts |
| BI | Power BI / DAX specification and governed KPI layer |
| Analytics | Python / statistical diagnostics |
| Forecasting | baseline-first time-series / ML evaluation |
| Data Quality | schema, domain, referential and reconciliation controls |
| Software Quality | pytest + Ruff |
| Delivery | Docker + GitHub Actions |
| Documentation | architecture, metric contract, data dictionary, assumptions, limitations, proof matrix |

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

The final model must reconcile to its synthetic source systems before downstream KPIs are considered valid.

---

## Proof standard

This flagship follows the Pretoria BI evidence rule:

> **No claim receives credit because it appears in a README. It receives credit only when the repository proves it.**

The final project must demonstrate five layers:

| Layer | Required proof |
|---|---|
| **Business Proof** | credible hospitality decision problem |
| **Analytical Proof** | conclusions supported by governed data and appropriate analysis |
| **Engineering Proof** | correct, testable and maintainable implementation |
| **Operational Proof** | reproducible pipeline, CI, failure handling and controls |
| **Value Proof** | quantified action logic with explicit assumptions and limitations |

---

## Reverse-test requirements

Before officialisation, the repository must prove that it can fail correctly.

At minimum:

- corrupt a source or target metric and require reconciliation to fail;
- inject invalid operational data and require Data Quality to block the pipeline;
- introduce an intentional KPI-definition conflict and require the metric contract test to reject it;
- compare forecasting against a naive baseline;
- verify that management conclusions change when the underlying driver is changed in a controlled scenario;
- prove that reported contribution reconciles to the documented component metrics.

A happy-path dashboard is not sufficient evidence.

---

## Repository architecture

```text
hospitality-intelligence-platform/
├── .github/workflows/
├── data/
│   └── sample/
├── docs/
├── sql/
├── src/hospitality_intelligence/
├── tests/
├── dashboards/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

Empty folders are not created for presentation. A directory appears only when it contains real evidence.

---

## Build status

**Phase 0 — architecture and contracts**

Current publication does **not** claim that the full platform is implemented yet.

The repository becomes **OFFICIAL** only after implementation, reverse testing, contradictory review and final scoring.

Target officialisation threshold: **92/100 minimum**.  
Internal flagship target: **95+/100 only if the evidence justifies it.**

---

<div align="center">

**Pretoria BI**

**Understand · Decide · Act · Measure**

</div>
