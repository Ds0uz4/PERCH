# PERCH — developer entry points. See CLAUDE.md §7 for the phase order these support.
.PHONY: help up down logs demo-good demo-bad demo-all test unit e2e fmt lint plots baseline clean

COMPOSE := docker compose

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Build and start the whole stack
	$(COMPOSE) up -d --build

down: ## Stop the stack and remove volumes
	$(COMPOSE) down -v

logs: ## Tail controller logs
	$(COMPOSE) logs -f controller

demo-good: ## Good canary: should ramp to 100% unattended
	./scenarios/scenario_good.sh

demo-bad: ## Broken canary (error spike): should roll back to 0% unattended
	./scenarios/scenario_bad_error_spike.sh

demo-all: ## Every scenario, back to back
	./scenarios/scenario_good.sh
	./scenarios/scenario_bad_error_spike.sh
	./scenarios/scenario_bad_latency.sh
	./scenarios/scenario_bad_slow_onset.sh
	./scenarios/scenario_bad_partial.sh

test: unit e2e ## All tests

unit: ## Unit tests — no Docker required
	pytest tests/test_decision.py -v

e2e: ## End-to-end tests — assumes `make up` has already run
	pytest tests/test_e2e.py -v

baseline: ## Naive threshold vs. statistical detector, blast-radius comparison
	python analysis/compare_baseline_vs_detector.py

plots: ## Regenerate plots from the latest decision log
	python analysis/plot_results.py

fmt: ## Format
	black .

lint: ## Lint
	ruff check .

clean: ## Remove run artifacts, keep the directory
	find results -type f ! -name .gitkeep -delete
