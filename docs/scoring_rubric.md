# Severe Scoring Rubric

## Purpose

This rubric is intentionally harsher than a normal portfolio review.

The repository is scored as if reviewed simultaneously by:

- a hospitality executive considering a consulting engagement;
- a Head of Data;
- a senior analytics engineer;
- a BI lead;
- a skeptical delivery partner.

## Weighted score

| Dimension | Weight |
|---|---:|
| Business problem quality | 12 |
| Hospitality domain depth | 12 |
| Analytical rigor | 12 |
| Data model & SQL | 10 |
| Python engineering | 8 |
| Data quality & reconciliation | 10 |
| BI / decision UX | 10 |
| Forecasting / statistics | 8 |
| Testing / CI / reproducibility | 8 |
| Documentation / communication | 5 |
| Commercial credibility | 5 |
| **Total** | **100** |

## Penalty rules

The following are explicit deductions:

- unsupported major README claim: **-5 each**;
- broken primary path or command: **-5**;
- material KPI definition inconsistency: **-8**;
- metric shown in BI but not reconcilable: **-8**;
- data leakage in forecasting: **-10**;
- fabricated client result or realized ROI: **automatic rejection**;
- credentials/private data committed: **automatic rejection**;
- critical test disabled to obtain green CI: **automatic rejection**;
- silent many-to-many/double-counting defect in headline metric: **score capped at 79**;
- forecast does not beat baseline but is still marketed as predictive value: **score capped at 84**;
- core pipeline not reproducible from documentation: **score capped at 89**.

## Bands

| Score | Interpretation |
|---|---|
| < 75 | reject / redesign |
| 75–84 | technically usable, not portfolio-grade |
| 85–91 | strong but not official |
| 92–95 | officialisable premium case |
| 96–100 | exceptional; requires unusually complete evidence |

## Rule

A score is never raised because of effort, visual polish or project size.

Only evidence counts.
