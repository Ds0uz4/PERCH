"""Ramp schedule and bake-time state machine — STUB (CLAUDE.md §5.4, Phase 3).

Stages and bake duration come from RampConfig; this module owns only the transitions:

    advance   -> move to the next stage, but only once bake_seconds have elapsed at the current
                 stage with no rollback decision in between
    rollback  -> canary weight to 0 immediately, and *stay there*. Terminal for the run: a later
                 clean window must not re-advance a canary that already tripped (CLAUDE.md §8)
    promote   -> reached the final stage (100%) and held it through a full bake
    hold      -> no weight change
"""

raise NotImplementedError("Phase 3: ramp state machine (CLAUDE.md §5.4)")
