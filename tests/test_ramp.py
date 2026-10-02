"""Ramp state machine tests. No Docker required."""

from __future__ import annotations

from config import RampConfig
from decision import Decision
from ramp import apply_decision, initial_state


CFG = RampConfig(stages=(5, 10, 25, 50, 100), bake_seconds=25)


def _decision(action: str) -> Decision:
    return Decision(action=action, reason="test", evidence={})  # type: ignore[arg-type]


def test_starts_at_first_stage() -> None:
    state = initial_state(CFG, now=0.0)
    assert state.canary_weight == 5
    assert state.stable_weight == 95


def test_does_not_advance_before_bake() -> None:
    state = initial_state(CFG, now=0.0)
    state, action = apply_decision(state, _decision("advance"), CFG, now=10.0)
    assert action == "hold"
    assert state.canary_weight == 5


def test_advances_after_bake() -> None:
    state = initial_state(CFG, now=0.0)
    state, action = apply_decision(state, _decision("advance"), CFG, now=25.0)
    assert action == "advance"
    assert state.canary_weight == 10


def test_rollback_is_terminal() -> None:
    state = initial_state(CFG, now=0.0)
    state, action = apply_decision(state, _decision("rollback"), CFG, now=5.0)
    assert action == "rollback"
    assert state.canary_weight == 0
    state, action = apply_decision(state, _decision("advance"), CFG, now=100.0)
    assert action == "hold"
    assert state.canary_weight == 0
    assert state.rolled_back


def test_promote_after_final_stage_bakes() -> None:
    state = initial_state(CFG, now=0.0)
    now = 0.0
    for expected in (10, 25, 50, 100):
        now += CFG.bake_seconds
        state, action = apply_decision(state, _decision("advance"), CFG, now)
        assert action == "advance"
        assert state.canary_weight == expected
    now += CFG.bake_seconds
    state, action = apply_decision(state, _decision("advance"), CFG, now)
    assert action == "promote"
    assert state.promoted
    assert state.canary_weight == 100
