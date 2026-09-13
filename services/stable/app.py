"""Stable/canary service — STUB (CLAUDE.md §5.1, Phase 1).

Both stable and canary run *this exact file*; behaviour differs only through environment
variables, so shipping a broken canary is a config change, never a code fork.

To implement:
  GET /health   -> 200 {"status": "ok"} always. Liveness only; never feeds rollout decisions.
  GET /work     -> simulated business logic, shaped by:
                     ERROR_RATE            float 0-1, probability of returning 500
                     LATENCY_MS_MEAN       injected sleep before responding
                     LATENCY_MS_JITTER     random spread around the mean
                     DEGRADE_ENDPOINT      if set, only this sub-path degrades (partial failure)
                     DEGRADE_RAMP_SECONDS  if set, fault ramps 0 -> configured value linearly over
                                           this many seconds from container start (slow onset)
  GET /metrics  -> prometheus_client exposition: a Counter for requests by status code and a
                   Histogram for request latency, every series labelled service="stable"|"canary"
                   from SERVICE_NAME read at startup.
"""

raise NotImplementedError("Phase 1: implement the service (CLAUDE.md §5.1)")
