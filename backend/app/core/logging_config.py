"""
Logging configuration for Isekai Wanderer backend.

Provides structured JSON logging and ensures mock service logs (email, discord)
are written to the logs/ directory.
"""

import logging
import os
import sys
from typing import Optional

# Default log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")


def ensure_log_dir(log_dir: Optional[str] = None) -> str:
    """Ensure the log directory exists; return its absolute path."""
    target = log_dir or LOG_DIR
    os.makedirs(target, exist_ok=True)
    return os.path.abspath(target)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with structured JSON-like formatting.

    Called during application startup (main.py lifespan).
    """
    ensure_log_dir()

    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S"

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    # File handler (general app log)
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, "app.log"), encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.addHandler(console_handler)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
