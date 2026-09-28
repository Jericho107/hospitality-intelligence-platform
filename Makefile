.PHONY: install lint test generate validate reverse-test clean

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
