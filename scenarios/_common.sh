#!/usr/bin/env bash
# Shared scenario plumbing — STUB (CLAUDE.md §5.6).
#
# Every scenario script performs these seven steps in this order; implement them here once:
#   1. reset the stack to a known state — canary weight 0, decision log rotated into results/
#   2. start the load generator in the background
#   3. deploy the canary configuration for this scenario (env vars + restart the canary container)
#   4. wait for a terminal state (weight 100%, or rollback to 0%) or a timeout
#   5. stop the load generator
#   6. run analysis/plot_results.py for this run
#   7. print a one-line summary: final weight, requests affected, time to terminal state
set -euo pipefail

scenario_run() {  # scenario_run <name> [ENV=VAL ...]
    echo "STUB: implement scenarios/_common.sh (CLAUDE.md §5.6)" >&2
    exit 1
}
