"""Logging configuration for the Ultimate Trading Solution."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory

from ultimate_trading_solution.core.config import settings


def configure_logging() -> None:
    """Configure application logging."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.environment == "production"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format=settings.logging.format,
        level=getattr(logging, settings.logging.level),
        handlers=_get_handlers(),
    )

    # Set third-party library log levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database.echo else logging.WARNING
    )


def _get_handlers() -> list[logging.Handler]:
    """Get logging handlers based on configuration."""
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.logging.level))
    handlers.append(console_handler)

    # File handler (if configured)
    if settings.logging.file_path:
        log_file = Path(settings.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count,
        )
        file_handler.setLevel(getattr(logging, settings.logging.level))
        handlers.append(file_handler)

    return handlers


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


# Initialize logging when module is imported
configure_logging()
