#!/usr/bin/env bash
# Good canary: behaves exactly like stable, should ramp to 100% unattended (CLAUDE.md §1).
set -euo pipefail
cd "$(dirname "$0")/.."
source scenarios/_common.sh

scenario_run "scenario_good" CANARY_ERROR_RATE=0.0 CANARY_LATENCY_MS_MEAN=40 CANARY_LATENCY_MS_JITTER=10
