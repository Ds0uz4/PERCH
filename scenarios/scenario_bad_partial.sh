#!/usr/bin/env bash
# Bad canary 4/4: only one endpoint is broken. Proves the load generator's traffic mix actually exercises the failing path.
set -euo pipefail
cd "$(dirname "$0")/.."
source scenarios/_common.sh

scenario_run "scenario_bad_partial" CANARY_ERROR_RATE=0.60 CANARY_DEGRADE_ENDPOINT=/work/checkout
