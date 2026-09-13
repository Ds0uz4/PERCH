"""Every magic number in PERCH, in one place, each with its justification (CLAUDE.md §6).

Values here are provisional defaults chosen for a laptop-scale demo; Phase 4/5 may retune them,
but the rule stands — nothing numeric may appear elsewhere in the controller without a line here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DecisionMode = Literal["naive_threshold", "tier1", "tier2_sprt"]


@dataclass(frozen=True)
class DecisionConfig:
    """Parameters of the rollback decision itself."""

    # Statistical detector (Tier 1) --------------------------------------------------------
    alpha: float = 0.05
    """False-positive rate for the two-proportion test. 5% is the conventional choice; a rolled-back
    good release costs a deploy cycle, so we are not paying for anything stricter."""

    beta: float = 0.10
    """False-negative rate, used by the Tier 2 SPRT boundaries. Missing a genuinely bad canary is
    the more expensive error, hence beta < alpha in effect (10% miss vs. 5% false alarm)."""

    min_samples_per_window: int = 200
    """No decision other than `hold` below this many canary requests in the window. At 5% traffic
    and ~50 rps this is roughly one 5s poll's worth of canary traffic — enough that a two-proportion
    test on a few-point error-rate difference is not being run on noise (CLAUDE.md §8)."""

    latency_tolerance: float = 1.5
    """Canary p95 may be up to 1.5x stable p95 before the latency signal fires. Below this, normal
    JIT/cache warm-up on a freshly started container is indistinguishable from real regression."""

    # Naive baseline (kept for the comparison in CLAUDE.md §5.7) ----------------------------
    naive_error_rate_delta: float = 0.05
    """Baseline rule: roll back when canary error rate exceeds stable's by 5 percentage points.
    Deliberately a round, undefensible number — that is the point of the comparison."""

    naive_latency_multiplier: float = 1.5
    """Baseline latency rule, matched to `latency_tolerance` so the comparison isolates the effect
    of the *statistics*, not of a differently-tuned threshold."""


@dataclass(frozen=True)
class RampConfig:
    """The progressive rollout schedule (CLAUDE.md §5.4)."""

    stages: tuple[int, ...] = (5, 10, 25, 50, 100)
    """Percent of traffic on the canary. Starts at 5% so that even a total canary failure caps the
    blast radius at ~5% of requests for one bake window; roughly doubles thereafter, which keeps the
    number of stages (and so total rollout time) small while never more than doubling exposure."""

    bake_seconds: int = 60
    """Seconds a stage must hold with no rollback before advancing. The trade-off: a longer bake
    accumulates more samples and so more confidence, but leaves a bad canary live longer and makes
    a good rollout slower. 60s at ~50 rps gives each stage well over `min_samples_per_window`
    canary requests even at the 5% stage."""

    rollback_is_terminal: bool = True
    """Once rolled back, the state machine stays at 0% until manually reset for the next scenario
    run — a later clean window must never silently re-advance a canary that already tripped the
    alarm (CLAUDE.md §8)."""


@dataclass(frozen=True)
class ControllerConfig:
    """Loop and I/O settings."""

    poll_interval_seconds: int = 5
    """One observe->decide->act cycle per 5s. Faster than the bake time so a bad canary is caught
    mid-stage, slower than the 2s Prometheus scrape so every poll sees fresh samples."""

    proxy_reload_debounce_seconds: int = 2
    """Never reload nginx more than once per 2s even if the loop asks more often — reloads drop
    in-flight connections and would contaminate the latency we are measuring (CLAUDE.md §8)."""

    decision_log_path: str = "/results/decision_log.jsonl"
    """Append-only JSON lines; one object per decision, carrying the full evidence dict."""

    decision: DecisionConfig = field(default_factory=DecisionConfig)
    ramp: RampConfig = field(default_factory=RampConfig)
