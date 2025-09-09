"""Logging configuration for ShellRosetta.

This module provides logging setup and configuration utilities.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration for ShellRosetta."""

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create logger
    logger_instance = logging.getLogger("shellrosetta")
    logger_instance.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger_instance.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger_instance.addHandler(file_handler)

    return logger_instance


def get_logger(name: str = "shellrosetta") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Default logger instance
logger = setup_logging()
