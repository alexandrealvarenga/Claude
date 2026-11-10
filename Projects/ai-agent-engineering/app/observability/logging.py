"""Structured Logging Configuration."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Common processors for all environments
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    processors.append(renderer)

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_handler = logging.StreamHandler(sys.stdout)
        uvicorn_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=renderer,
                foreign_pre_chain=processors[:-1],
            )
        )
        uvicorn_logger.addHandler(uvicorn_handler)
        uvicorn_logger.setLevel(log_level)

    # Root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Optional logger name for context.

    Returns:
        Configured structlog logger.
    """
    logger = structlog.get_logger()

    if name:
        logger = logger.bind(logger_name=name)

    return logger


class LoggerMixin:
    """Mixin class to add logger capability to any class."""

    @property
    def log(self) -> structlog.stdlib.BoundLogger:
        """Get logger bound to the class name."""
        return get_logger(self.__class__.__name__)
