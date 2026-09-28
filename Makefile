.PHONY: install lint test generate validate up down ingest reconcile transform warehouse-validate metric-contracts metrics metric-validate pipeline reverse-test clean

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

generate:
	python -m hospitality_intelligence.generate_synthetic_data \
		--output-dir data/sample \
		--days 60 \
		--seed 42 \
		--anchor 2026-09-01T00:00:00+00:00 \
		--scenario margin_leakage

validate:
	python -m hospitality_intelligence.validate_sources --data-dir data/sample

up:
	docker compose up -d --wait

down:
	docker compose down

ingest:
	python -m hospitality_intelligence.ingest --data-dir data/sample

reconcile:
	python -m hospitality_intelligence.reconciliation --data-dir data/sample

transform:
	python -m hospitality_intelligence.transform

warehouse-validate:
	python -m hospitality_intelligence.validate_warehouse

metric-contracts:
	python -m hospitality_intelligence.metric_contracts

metrics:
	python -m hospitality_intelligence.build_metrics

metric-validate:
	python -m hospitality_intelligence.validate_metrics

pipeline: generate validate up ingest reconcile transform warehouse-validate metric-contracts metrics metric-validate

reverse-test: generate validate
	python -m hospitality_intelligence.failure_injection \
		--data-dir data/sample \
		--case pos_revenue_mismatch
	@if python -m hospitality_intelligence.validate_sources --data-dir data/sample; then \
		echo "Expected source validation to fail after controlled mismatch."; \
		exit 1; \
	else \
		echo "Controlled mismatch detected as expected."; \
	fi
	$(MAKE) generate
	$(MAKE) validate

clean:
	rm -rf data/sample
