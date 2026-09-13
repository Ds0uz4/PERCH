"""Renders proxy/nginx.conf.j2 and reloads nginx — STUB (CLAUDE.md §5.2, Phase 1).

Mechanism (documented in README.md): the controller and the proxy share the `proxy-conf` Docker
volume. This module renders the template into that volume, then triggers `nginx -s reload` in the
proxy container over the mounted Docker socket.

Two things must hold:
  * Reloads are debounced to at most one per ControllerConfig.proxy_reload_debounce_seconds, even
    when the control loop ticks faster — reloading on every tick drops connections under load and
    corrupts the very latency measurements the controller is reading (CLAUDE.md §8).
  * A zero weight must be emitted as `down`, not `weight=0`; nginx treats weight=0 as invalid.
"""

raise NotImplementedError("Phase 1: template render + debounced reload (CLAUDE.md §5.2)")
