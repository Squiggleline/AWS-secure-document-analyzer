"""
Logging Utility
===============

Provides a consistent, structured logging configuration for the Lambda
function. Reads the ``LOG_LEVEL`` environment variable (default: INFO).
"""

import logging
import os

_DEFAULT_LOG_LEVEL = "INFO"


def get_logger(name: str = "secure-document-analyzer") -> logging.Logger:
    """
    Return a configured logger.

    Parameters:
        name (str): Logger name. Defaults to ``secure-document-analyzer``.

    Returns:
        logging.Logger: A logger with the configured level.
    """
    level = os.environ.get("LOG_LEVEL", _DEFAULT_LOG_LEVEL).upper()
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger