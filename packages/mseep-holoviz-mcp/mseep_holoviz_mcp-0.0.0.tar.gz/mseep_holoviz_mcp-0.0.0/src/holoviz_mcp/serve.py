#!/usr/bin/env python3
"""Serve Panel apps with configurable arguments."""

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Serve all Panel apps in the apps directory."""
    apps_dir = Path(__file__).parent / "apps"
    app_files = [str(f) for f in apps_dir.glob("*.py") if f.name != "__init__.py"]

    if not app_files:
        logger.warning("No Panel apps found in apps directory")
        return

    # Use python -m panel to ensure we use the same Python environment
    cmd = [sys.executable, "-m", "panel", "serve", *app_files, *sys.argv[1:]]
    logger.info(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
