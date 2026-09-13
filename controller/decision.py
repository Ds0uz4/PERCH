"""The rollback decision — STUB (CLAUDE.md §5.3, Phase 3/4).

Everything in this module must stay **pure**: no I/O, no globals, no clock reads. The grader looks
here for rigour, and `tests/test_decision.py` can only assert exact decisions on synthetic samples
if these functions are deterministic functions of their arguments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from config import DecisionConfig, DecisionMode

Action = Literal["hold", "advance", "rollback", "promote"]


@dataclass(frozen=True)
class MetricSample:
    """One service's behaviour over one observation window."""

    service: str  # "stable" | "canary"
    window_start: float
    window_end: float
    request_count: int
    error_count: int
    p95_latency_ms: float


@dataclass(frozen=True)
class Decision:
    action: Action
    reason: str
    evidence: dict  # everything needed to reconstruct this decision from the log alone


def evaluate(
    canary: MetricSample, stable: MetricSample, cfg: DecisionConfig, mode: DecisionMode
) -> Decision:
    """Dispatch on DECISION_MODE so the naive baseline stays runnable for CLAUDE.md §5.7."""
    raise NotImplementedError("Phase 4: dispatch to the mode implementations below")


def evaluate_naive_threshold(
    canary: MetricSample, stable: MetricSample, cfg: DecisionConfig
) -> Decision:
    """Baseline rule (Phase 3): rollback if canary error rate exceeds stable's by more than
    cfg.naive_error_rate_delta, or canary p95 exceeds stable p95 * cfg.naive_latency_multiplier.
    No confidence interval, no sample-size floor — that is exactly what the comparison measures."""
    raise NotImplementedError("Phase 3: naive threshold")


def evaluate_tier1(canary: MetricSample, stable: MetricSample, cfg: DecisionConfig) -> Decision:
    """Two-proportion test (Wilson score interval) on error rate + percentile ratio on latency.

    Returns 'rollback' only if the interval for (canary_error_rate - stable_error_rate) excludes 0
    in the unfavourable direction, OR canary p95 exceeds stable p95 * cfg.latency_tolerance, in
    either case with at least cfg.min_samples_per_window canary requests behind the comparison.

    Below that sample floor the answer is always 'hold' — never a guess (CLAUDE.md §8).
    Record each signal's evidence separately so the log is auditable metric by metric.
    """
    raise NotImplementedError("Phase 4: Wilson-interval two-proportion test + latency ratio")


def evaluate_tier2_sprt(
    canary: MetricSample, stable: MetricSample, cfg: DecisionConfig
) -> Decision:
    """Stretch (Phase 6): maintain a running log-likelihood ratio over each new success/failure
    observation in the bake window and compare it against boundaries derived from cfg.alpha and
    cfg.beta. Implement only once Tier 1 is fully working and tested."""
    raise NotImplementedError("Phase 6 (stretch): SPRT")
