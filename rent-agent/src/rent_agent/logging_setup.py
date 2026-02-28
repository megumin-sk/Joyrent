"""Logging setup for JoyRent Agent."""

from __future__ import annotations

import logging
import os
import sys


def configure_logging() -> None:
    """Configure project logging once for both CLI and uvicorn startup paths."""
    level_name = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    project_logger = logging.getLogger("rent_agent")

    # Idempotent guard: avoid duplicate handlers under reload mode.
    if any(getattr(handler, "name", "") == "rent_agent_stderr" for handler in project_logger.handlers):
        project_logger.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.name = "rent_agent_stderr"
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    project_logger.addHandler(handler)
    project_logger.setLevel(level)
    project_logger.propagate = False

    # Reduce third-party noise.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
