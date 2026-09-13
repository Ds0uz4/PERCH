"""Controller loop — STUB (CLAUDE.md §5.5, Phase 3).

    loop every POLL_INTERVAL_SECONDS:
        query Prometheus for both services' MetricSample over the current bake window
        if not enough samples yet: continue          # never decide on noise
        decision = evaluate(canary, stable, cfg, mode)
        apply decision to the ramp state machine
        if weight changed: render nginx.conf.j2, reload proxy (debounced)
        append decision + evidence to /results/decision_log.jsonl (one JSON object per line)

The log line is the project's primary artifact: timestamp, current weight, both services' error
rate with confidence interval, both p95 latencies, the action and the reason. It has to be enough
on its own to reconstruct why the controller did what it did.
"""

raise NotImplementedError("Phase 3: asyncio observe->decide->act->log loop (CLAUDE.md §5.5)")
