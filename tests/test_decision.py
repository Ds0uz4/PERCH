"""Unit tests for controller/decision.py. No Docker required."""

from __future__ import annotations

from config import DecisionConfig
from decision import MetricSample, evaluate, evaluate_naive_threshold, evaluate_tier1

CFG = DecisionConfig()


def sample(service: str, n: int, errors: int, p95: float = 40.0) -> MetricSample:
    return MetricSample(
        service=service,
        window_start=0.0,
        window_end=1.0,
        request_count=n,
        error_count=errors,
        p95_latency_ms=p95,
    )


def test_clearly_fine_canary_advances() -> None:
    decision = evaluate(
        sample("canary", 200, 0), sample("stable", 200, 0), CFG, "tier1"
    )
    assert decision.action == "advance"


def test_clearly_broken_error_rate_rolls_back() -> None:
    decision = evaluate(
        sample("canary", 200, 60), sample("stable", 200, 0), CFG, "tier1"
    )
    assert decision.action == "rollback"
    assert "error" in decision.reason.lower()


def test_clearly_broken_latency_rolls_back() -> None:
    decision = evaluate(
        sample("canary", 200, 0, p95=400),
        sample("stable", 200, 0, p95=40),
        CFG,
        "tier1",
    )
    assert decision.action == "rollback"
    assert "p95" in decision.reason.lower()


def test_too_few_samples_holds_even_if_ratio_looks_bad() -> None:
    decision = evaluate_tier1(
        sample("canary", 10, 10), sample("stable", 200, 0), CFG
    )
    assert decision.action == "hold"
    assert "holding" in decision.reason.lower()


def test_borderline_error_rate_holds() -> None:
    # 12/200 = 6% vs 2/200 = 1%. Point estimate looks worse; Wilson CI still
    # includes 0, so the honest answer is "not sure yet".
    decision = evaluate_tier1(
        sample("canary", 200, 12), sample("stable", 200, 2), CFG
    )
    assert decision.action == "hold"


def test_naive_fires_on_noisy_sample_that_tier1_holds() -> None:
    noisy_canary = sample("canary", 10, 2)  # 20% errors on 10 requests
    stable = sample("stable", 10, 0)
    naive = evaluate_naive_threshold(noisy_canary, stable, CFG)
    tier1 = evaluate_tier1(noisy_canary, stable, CFG)
    assert naive.action == "rollback"
    assert tier1.action == "hold"


def test_dispatch_naive_mode() -> None:
    decision = evaluate(
        sample("canary", 200, 0), sample("stable", 200, 0), CFG, "naive_threshold"
    )
    assert decision.action == "advance"


def test_sprt_rolls_back_on_loud_fault() -> None:
    decision = evaluate(
        sample("canary", 200, 60), sample("stable", 200, 0), CFG, "tier2_sprt"
    )
    assert decision.action == "rollback"
