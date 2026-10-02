"""Render nginx.conf.j2 into the shared volume and reload the proxy.

A zero canary weight becomes `down`, not `weight=0` (nginx treats 0 as invalid).
Reloads are debounced so a busy control loop cannot drop connections and
contaminate the latency it is measuring.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class ProxyWriter:
    def __init__(
        self,
        template_path: str,
        output_path: str,
        proxy_container: str,
        debounce_seconds: float,
    ) -> None:
        self.template_path = Path(template_path)
        self.output_path = Path(output_path)
        self.proxy_container = proxy_container
        self.debounce_seconds = debounce_seconds
        self._last_reload = 0.0
        self._applied: tuple[int, int] | None = None
        env = Environment(
            loader=FileSystemLoader(str(self.template_path.parent)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )
        self._template = env.get_template(self.template_path.name)

    def render(self, stable_weight: int, canary_weight: int) -> str:
        return self._template.render(
            stable_weight=int(stable_weight),
            canary_weight=int(canary_weight),
        )

    def apply(self, stable_weight: int, canary_weight: int, force: bool = False) -> bool:
        """Write config and reload if weights changed. Returns True if reloaded."""
        desired = (int(stable_weight), int(canary_weight))
        text = self.render(*desired)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.output_path.read_text(encoding="utf-8") if self.output_path.exists() else ""
        if existing != text:
            self.output_path.write_text(text, encoding="utf-8")

        if not force and self._applied == desired:
            return False

        now = time.monotonic()
        wait = self.debounce_seconds - (now - self._last_reload)
        if wait > 0:
            time.sleep(wait)

        self._reload()
        self._last_reload = time.monotonic()
        self._applied = desired
        return True

    def _reload(self) -> None:
        test = subprocess.run(
            ["docker", "exec", self.proxy_container, "nginx", "-t"],
            check=False,
            capture_output=True,
            text=True,
        )
        if test.returncode != 0:
            raise RuntimeError(
                f"nginx -t failed:\n{test.stdout}\n{test.stderr}"
            )
        reload = subprocess.run(
            ["docker", "exec", self.proxy_container, "nginx", "-s", "reload"],
            check=False,
            capture_output=True,
            text=True,
        )
        if reload.returncode != 0:
            raise RuntimeError(
                f"nginx reload failed:\n{reload.stdout}\n{reload.stderr}"
            )
