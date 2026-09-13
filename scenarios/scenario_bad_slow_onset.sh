#!/usr/bin/env bash
# Bad canary 3/4: degradation ramps in gradually over the bake window. Proves the controller is not just sampling a single instant.
set -euo pipefail
cd "$(dirname "$0")/.."
source scenarios/_common.sh

scenario_run "scenario_bad_slow_onset" CANARY_ERROR_RATE=0.30 CANARY_DEGRADE_RAMP_SECONDS=120
