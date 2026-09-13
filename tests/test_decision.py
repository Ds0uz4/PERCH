"""Unit tests for controller/decision.py — STUB (CLAUDE.md §5.3, Phase 4).

Must NOT require Docker. Feeds synthetic MetricSamples to the pure decision functions and asserts
exact decisions. Required cases:

  * clearly-fine canary          -> advance (eventually promote)
  * clearly-broken canary        -> rollback
  * borderline / ambiguous       -> hold, never a guess
  * too few samples to decide    -> hold, regardless of how bad the ratio looks

Plus, for the naive mode, a case where the naive rule fires on a small noisy sample that tier1
correctly holds on — that asymmetry is what the baseline comparison is measuring.
"""

import pytest

pytest.skip("Phase 4: decision tests not written yet", allow_module_level=True)
