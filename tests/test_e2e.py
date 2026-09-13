"""End-to-end tests against the live stack — STUB (CLAUDE.md §6, Phase 3).

Assumes `make up` has already run; hits real HTTP endpoints rather than inspecting generated
config files. Suggested coverage:

  * /health and /work respond on both services directly and through the proxy
  * both services expose /metrics with the expected series and service= label
  * Prometheus has both targets up and returns sane error-rate and latency values
  * setting a weight through the controller visibly shifts the observed traffic split at the proxy
  * services/stable/app.py and services/canary/app.py are byte-identical
"""

import pytest

pytest.skip("Phase 3: e2e tests not written yet", allow_module_level=True)
