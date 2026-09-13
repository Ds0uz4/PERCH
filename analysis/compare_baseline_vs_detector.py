"""Naive threshold vs. statistical detector — STUB (CLAUDE.md §5.7, Phase 5).

The single most important comparison in the project; do not skip it under time pressure.

Runs scenarios/scenario_bad_error_spike.sh twice against the same canary fault:
    once with DECISION_MODE=naive_threshold
    once with DECISION_MODE=tier1
and reports the difference in **blast radius** — requests served by the bad canary before rollback —
plus time to rollback, as a table and an overlaid plot.

Repeat each arm >=5 times and report mean and variance, not a single number (CLAUDE.md §2).
"""

raise NotImplementedError("Phase 5: baseline comparison (CLAUDE.md §5.7)")
