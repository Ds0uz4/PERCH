#!/usr/bin/env bash
# Bad canary 1/4: uniformly elevated error rate. The primary rollback demo, and the scenario the naive-vs-statistical comparison is run on.
set -euo pipefail
cd "$(dirname "$0")/.."
source scenarios/_common.sh

scenario_run "scenario_bad_error_spike" CANARY_ERROR_RATE=0.30 CANARY_LATENCY_MS_MEAN=40 CANARY_LATENCY_MS_JITTER=10
