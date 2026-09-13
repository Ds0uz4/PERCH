#!/usr/bin/env bash
# Bad canary 2/4: latency only, error rate unchanged. Proves the latency signal does real work rather than riding along with the error check.
set -euo pipefail
cd "$(dirname "$0")/.."
source scenarios/_common.sh

scenario_run "scenario_bad_latency" CANARY_ERROR_RATE=0.0 CANARY_LATENCY_MS_MEAN=400 CANARY_LATENCY_MS_JITTER=120
