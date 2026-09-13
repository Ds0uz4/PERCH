"""Plots for one scenario run — STUB (CLAUDE.md §2, Phase 5).

Reads results/decision_log.jsonl (and Prometheus range queries where finer resolution is needed)
and writes PNGs into results/:

  * traffic weight vs. time, with the rollback/promotion instant marked
  * error rate vs. time, canary and stable on the same axes
  * p95 latency vs. time, canary and stable on the same axes

Mark each ramp stage boundary so the bake windows are visible — the point of the plot is to show
the decision being made, not just the metric moving.
"""

raise NotImplementedError("Phase 5: plots (CLAUDE.md §2)")
