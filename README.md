# PERCH — Progressive Evaluation & Rollback Controller for Health-driven rollout

A canary release system that runs on a laptop under Docker Compose.

Two versions of one HTTP service sit behind **nginx weighted routing**. A small
controller scrapes **success rate and p95 latency** from Prometheus, compares
canary against stable, and **moves the traffic weights by itself**:

- a good canary is promoted to **100%** with no one watching a dashboard
- a bad canary is rolled back to **0%** before most users see it

That is the whole product. Everything else (Wilson intervals, bake windows,
decision logs, plots) exists so you can *see why* it moved the weight.

## What you will see

| Demo | What is shipped | What the controller does |
|---|---|---|
| `python scenarios/run.py good` | Canary identical to stable | 5% → 10% → 25% → 50% → **100%** |
| `python scenarios/run.py bad-error` | Canary returns HTTP 500 on 30% of requests | Catches it at 5% and **rolls back to 0%** |

## Architecture

```
load generator
      │  constant ~50 rps at /work  (open-loop: does not slow down when canary is slow)
      ▼
  nginx (weighted round-robin)
      ├── stable:8000     weight = 100 − canary_weight
      └── canary:8000     weight = canary_weight   (or `down` when weight is 0)
              │
              ├── GET /metrics  ──► Prometheus (scrape every 2s)
              │
              └── controller, every 5s:
                    1. query error rate + p95 for both services
                    2. decide: hold / advance / rollback
                    3. if the weight changed, rewrite nginx.conf and reload
                    4. append one JSON line of evidence to results/decision_log.jsonl
```

Zero-weight is emitted as `down`, not `weight=0`. nginx treats `weight=0` as invalid
and would keep sending traffic.

## How the decision works

The code to read first is `controller/decision.py`. It is a pure function:
`MetricSample × MetricSample × config → hold | advance | rollback`. No I/O.

**Tier 1 (default, `DECISION_MODE=tier1`)**

1. If the canary has fewer than `min_samples_per_window` (40) requests in the
   bake window, **hold**. Never guess on noise.
2. Build a Wilson score interval for `(canary_error_rate − stable_error_rate)`.
   Rollback only if that interval sits **entirely above 0**.
3. Rollback if canary p95 latency is more than `1.5×` stable p95.
4. If the interval still overlaps 0 but the canary *looks* a bit worse, **hold**
   (do not advance a maybe-broken release; do not roll back a maybe-fine one).
5. Otherwise **advance**. The ramp state machine in `controller/ramp.py` only
   bumps the weight after the current stage has been healthy for `bake_seconds`.

A rollback is **terminal** for that run. A later clean window cannot sneak the
bad canary back onto the path.

**Naive baseline (`DECISION_MODE=naive_threshold`)**

Rollback if the point estimates differ by more than 5 percentage points of
errors, or p95 exceeds 1.5×. No sample-size floor. This is what the statistical
rule is compared against: it will fire on ten unlucky requests that tier 1
correctly holds on. See `tests/test_decision.py`.

## Layout

| Path | Role |
|---|---|
| `services/stable/app.py` and `services/canary/app.py` | **Byte-identical** FastAPI apps. Behaviour differs only via env vars. |
| `proxy/nginx.conf.j2` | Weighted upstream template the controller renders |
| `controller/` | Observe → decide → act → log |
| `loadgen/generate_traffic.py` | Constant-rate client |
| `prometheus/prometheus.yml` | Scrapes both services every 2s |
| `scenarios/run.py` | Demo driver (Windows and Unix) |
| `results/` | Decision log, loadgen log, `rollout.png` |

Shipping a broken canary is **never a code fork**. The scenario runner restarts
the canary container with `CANARY_ERROR_RATE=0.30` (or a latency / partial /
slow-onset fault).

## Local setup

Docker is required. A venv is only needed for unit tests and plots.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Quick start

```powershell
docker compose up -d --build
python -m pytest tests/test_decision.py tests/test_ramp.py tests/test_proxy_writer.py -v

# Direction 1 — good update, traffic walks to 100% by itself (~2 minutes)
python scenarios/run.py good

# Direction 2 — broken update, automatic rollback at the 5% stage
python scenarios/run.py bad-error
```

Or with make, if you have it:

```text
make up
make unit
make demo-good
make demo-bad
make down
```

Watch the controller while a demo runs:

```powershell
docker compose logs -f controller
```

When it finishes, open `results/rollout.png`. Three stacked charts: canary
weight, error rate (both versions), p95 latency (both versions). Rollback and
promote instants are marked.

## Other faults

```text
python scenarios/run.py bad-latency      # slow, not erroring
python scenarios/run.py bad-slow-onset   # 30% errors, ramped in over 120s
python scenarios/run.py bad-partial      # only /work/checkout is broken
python scenarios/run.py all
```

## Tuning

Every number lives in `controller/config.py` with a comment saying why it is
that number, and can be overridden by environment variables (see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `RAMP_STAGES` | `5,10,25,50,100` | Canary traffic percentages |
| `RAMP_BAKE_SECONDS` | `25` | Healthy time required before the next stage |
| `MIN_SAMPLES_PER_WINDOW` | `40` | Sample floor for any non-hold decision |
| `LATENCY_TOLERANCE` | `1.5` | Canary p95 / stable p95 rollback ratio |
| `DECISION_MODE` | `tier1` | `tier1`, `naive_threshold`, or `tier2_sprt` |
| `LOADGEN_RPS` | `50` | Offered rate during demos |

## Tests

- `tests/test_decision.py` — synthetic metrics, exact actions, including the
  naive-vs-tier1 disagreement on a tiny noisy sample
- `tests/test_ramp.py` — bake time, terminal rollback, promote at 100%
- `tests/test_proxy_writer.py` — `weight=0` is rendered as `down`
- `tests/test_e2e.py` — live HTTP/Prometheus checks; skips if the stack is down

## Reading a decision

One line of `results/decision_log.jsonl`:

```json
{
  "ts": "2026-10-02T17:41:02+00:00",
  "canary_weight": 0,
  "action": "rollback",
  "reason": "canary error 0.312 significantly worse than stable 0.000 (Δ CI [0.21, 0.41] excludes 0)",
  "canary": {"n": 58, "errors": 18, "error_rate": 0.31, "p95_ms": 52.1},
  "stable": {"n": 1102, "errors": 0, "error_rate": 0.0, "p95_ms": 48.4}
}
```

That line is enough to reconstruct the decision without the rest of the system.
