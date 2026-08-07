"""Compatibility entry point; screenshots are captured by Playwright."""

import subprocess


raise SystemExit(subprocess.call(["npm", "run", "screenshots"], cwd="frontend"))
