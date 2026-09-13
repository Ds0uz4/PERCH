"""Constant-rate load generator — STUB (CLAUDE.md §3, Phase 1).

Drives a steady request rate at the proxy for the whole duration of every scenario, so that the
traffic split the controller is adjusting is always carrying real requests.

To implement (asyncio + httpx):
  --target   proxy base URL              (default from LOADGEN_TARGET)
  --rps      constant offered rate       (default from LOADGEN_RPS)
  --duration seconds, or run until SIGTERM from the scenario script
  --mix      relative weights across /work sub-paths, so the "partial failure" scenario actually
             exercises the endpoint that is broken

Rate must stay *constant* regardless of response latency — an open-loop generator. A closed-loop
one would slow down exactly when the canary degrades, hiding the degradation from the controller.
Write per-request outcomes to results/ so blast radius (requests served by the canary before
rollback) can be counted client-side as well as from Prometheus.
"""

raise NotImplementedError("Phase 1: open-loop asyncio load generator")
