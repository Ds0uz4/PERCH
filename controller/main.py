"""Observe → decide → act → log.

The loop is the whole controller:

    every POLL_INTERVAL_SECONDS
        pull canary + stable MetricSamples from Prometheus
        evaluate()  (pure)
        apply_decision() to the ramp state machine
        if the weight changed: render nginx.conf and reload
        append one JSON line to /results/decision_log.jsonl
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from config import ControllerConfig, DecisionMode, from_env
from decision import Decision, evaluate
from metrics import PrometheusClient
from proxy_writer import ProxyWriter
from ramp import RampState, apply_decision, initial_state


def _log_line(
    state: RampState,
    canary,
    stable,
    evaluated: Decision,
    taken,
    now: float,
) -> dict:
    return {
        "ts": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
        "unix": now,
        "canary_weight": state.canary_weight,
        "stable_weight": state.stable_weight,
        "rolled_back": state.rolled_back,
        "promoted": state.promoted,
        "evaluated_action": evaluated.action,
        "action": taken,
        "reason": evaluated.reason,
        "canary": {
            "n": canary.request_count,
            "errors": canary.error_count,
            "error_rate": canary.error_rate,
            "p95_ms": canary.p95_latency_ms,
        },
        "stable": {
            "n": stable.request_count,
            "errors": stable.error_count,
            "error_rate": stable.error_rate,
            "p95_ms": stable.p95_latency_ms,
        },
        "evidence": evaluated.evidence,
    }


def _write_status(path: Path, state: RampState, taken: str, reason: str) -> None:
    path.write_text(
        json.dumps(
            {
                "canary_weight": state.canary_weight,
                "stable_weight": state.stable_weight,
                "rolled_back": state.rolled_back,
                "promoted": state.promoted,
                "last_action": taken,
                "reason": reason,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def run(cfg: ControllerConfig) -> None:
    mode: DecisionMode = os.environ.get("DECISION_MODE", "tier1")  # type: ignore[assignment]
    if mode not in ("naive_threshold", "tier1", "tier2_sprt"):
        raise SystemExit(f"invalid DECISION_MODE={mode!r}")

    log_path = Path(cfg.decision_log_path)
    status_path = log_path.with_name("status.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    prom = PrometheusClient(os.environ.get("PROMETHEUS_URL", "http://prometheus:9090"))
    writer = ProxyWriter(
        template_path=os.environ.get("TEMPLATE_PATH", "/app/nginx.conf.j2"),
        output_path=os.environ.get("NGINX_CONF_PATH", "/etc/nginx/conf.d/default.conf"),
        proxy_container=os.environ.get("PROXY_CONTAINER", "perch-proxy"),
        debounce_seconds=cfg.proxy_reload_debounce_seconds,
    )

    now = time.time()
    state = initial_state(cfg.ramp, now)
    print(
        f"controller starting mode={mode} first_weight={state.canary_weight}% "
        f"stages={list(cfg.ramp.stages)} bake={cfg.ramp.bake_seconds}s",
        flush=True,
    )
    writer.apply(state.stable_weight, state.canary_weight, force=True)

    window = cfg.ramp.bake_seconds
    while True:
        loop_start = time.time()
        try:
            canary = prom.sample("canary", window)
            stable = prom.sample("stable", window)
            evaluated = evaluate(canary, stable, cfg.decision, mode)
            new_state, taken = apply_decision(state, evaluated, cfg.ramp, loop_start)
            if new_state.canary_weight != state.canary_weight:
                writer.apply(new_state.stable_weight, new_state.canary_weight)
                print(
                    f"weight {state.canary_weight}% → {new_state.canary_weight}% "
                    f"action={taken} reason={evaluated.reason}",
                    flush=True,
                )
            state = new_state
            record = _log_line(state, canary, stable, evaluated, taken, loop_start)
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
            _write_status(status_path, state, taken, evaluated.reason)
        except Exception as exc:
            print(f"controller tick failed: {exc!r}", flush=True)

        elapsed = time.time() - loop_start
        time.sleep(max(0.0, cfg.poll_interval_seconds - elapsed))


if __name__ == "__main__":
    run(from_env())
