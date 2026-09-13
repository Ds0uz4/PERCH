# PERCH — Progressive Evaluation & Rollback Controller for Health-driven rollout

A canary release system that runs entirely on a laptop under Docker Compose. Two versions of one
HTTP service sit behind a weighted nginx proxy; a controller continuously compares the canary's
error rate and latency against stable's and moves the traffic weight on its own — promoting a good
release to 100% and rolling a bad one back to 0% with no human touching a dashboard.

## Architecture

```
loadgen ──> nginx (weighted split) ──> stable  ──/metrics──┐
                    ▲              └──> canary  ──/metrics──┴──> Prometheus
                    │                                              │
                    └────── rewrite weights + reload ── controller ─┘
                                                            │
                                                            └──> results/decision_log.jsonl
```

## Local setup

The services, proxy, and controller install their own dependencies inside their Docker images.
The virtualenv is only for what runs on the host: tests, formatters, the load generator, and the
analysis scripts.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # .env is gitignored; edit it for local overrides
```

## Quick start (once implemented)

```bash
make up          # bring the stack up
make demo-good   # good canary: ramps to 100% unattended
make demo-bad    # broken canary: rolls back to 0% unattended
make test        # unit tests + e2e tests against the live stack
make down
```

## Layout

| Path | What lives here |
|---|---|
| `services/stable`, `services/canary` | The same FastAPI app; behaviour differs only via env vars |
| `proxy/` | nginx image + `nginx.conf.j2`, rendered with live weights by the controller |
| `controller/` | The observe → decide → act → log loop, plus the decision statistics |
| `loadgen/` | Constant background request rate against the proxy during every scenario |
| `prometheus/` | Scrape config for both services |
| `scenarios/` | One script per demo: good canary + four failure signatures |
| `analysis/` | Plot generation and the naive-vs-statistical blast-radius comparison |
| `predictions/` | Pre-registered prediction, committed before the first chaos run |
| `results/` | Decision logs, CSVs, PNGs from real runs (contents gitignored) |
| `implementation-plans/` | `baseline-implementation-plan.md` and `stretch-upgrades.md` |

## How the controller changes the traffic weight

Decided: the controller and the proxy **share a Docker volume** holding the rendered `nginx.conf`.
The controller renders `proxy/nginx.conf.j2` into that volume and signals a reload; reloads are
debounced to at most one per 2s so a busy control loop cannot drop connections and contaminate the
latency measurements it is reading (`CLAUDE.md` §5.2, §8).

## Design notes

Every tunable constant — ramp stages, bake durations, minimum sample counts, significance levels —
lives in `controller/config.py` with an inline justification, so each one can be defended in the
report rather than appearing as an unexplained magic number.
