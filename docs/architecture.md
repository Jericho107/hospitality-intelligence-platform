# Architecture

## Design principle

The platform separates the **source-faithful landing state** from the **typed analytical state**.

That boundary matters because a dimensional model should not double as the evidence that ingestion was faithful.

```text
SEEDED SYNTHETIC OPERATING SOURCES
        │
        ├── PMS
        ├── POS
        ├── procurement / inventory
        ├── labour
        └── budget
        │
        ▼
PYDANTIC + CROSS-SOURCE CONTRACTS
        │
        ▼
RAW POSTGRESQL LANDING
all source columns preserved as text
        │
        ├── exact row count
        └── canonical ordered SHA-256
        │
        ▼
SOURCE ↔ RAW RECONCILIATION
        │
        ▼
TYPED DIMENSIONAL MODEL
        │
        ├── dimensions
        └── grain-specific facts
        │
        ▼
RAW ↔ ANALYTICS CONTROLS
row counts + operational totals + financial totals
        │
        ▼
GOVERNED KPI / BI / DIAGNOSTIC LAYERS
future phases
```

## Why raw tables are text

The raw schema intentionally stores the CSV representation as text.

This provides a source-faithful landing state that can be hashed against the source files without numeric formatting or type coercion changing the evidence.

Typing and constraints are applied in the `analytics` schema.

## Failure boundaries

Phase 2 reverse-tests two independent boundaries:

1. **source → raw**: mutate a raw PostgreSQL value while the source CSV remains unchanged; exact reconciliation must fail.
2. **raw → analytics**: mutate one analytical fact after a clean transform; warehouse validation must fail.

Recovery requires reloading or rebuilding from the preceding trusted layer.

## Current boundary

This architecture proves ingestion and dimensional transformation. It does not yet prove KPI definitions, Power BI behavior, management conclusions, forecasting or business impact.
