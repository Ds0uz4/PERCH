"""Simple script to reload nginx when config changes.

Run this in a separate terminal to automatically reload nginx when
the controller writes a new configuration.
"""

import os
import subprocess
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "proxy-conf" / "default.conf"
CONTAINER = "perch-proxy"

print(f"Watching {CONFIG_PATH} for changes...")
print(f"Will reload nginx in {CONTAINER} when config changes.")
print("Press Ctrl+C to stop.")

last_hash = None

while True:
    try:
        if CONFIG_PATH.exists():
            current_hash = CONFIG_PATH.read_text().__hash__()
            if last_hash is not None and current_hash != last_hash:
                print(f"Config changed, reloading nginx in {CONTAINER}...")
                result = subprocess.run(
                    ["docker", "compose", "exec", "-T", CONTAINER, "nginx", "-s", "reload"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print("nginx reloaded successfully")
                else:
                    print(f"WARNING: nginx reload failed: {result.stderr}")
            last_hash = current_hash
    except Exception as e:
        print(f"Error checking config: {e}")
    
    time.sleep(2)
