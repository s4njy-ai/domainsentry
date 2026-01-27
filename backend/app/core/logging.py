"""
Structured logging configuration for DomainSentry.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

import structlog
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, filter_by_level
from structlog.threadlocal import wrap_dict


def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add ISO 8601 timestamp to log events.
    """
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_environment(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add environment information to log events.
    """
    from app.core.config import settings
    
    event_dict["environment"] = settings.ENVIRONMENT
    event_dict["service"] = "domainsentry-backend"
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging with structlog.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            filter_by_level,
            add_log_level,
            add_timestamp,
            add_environment,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        context_class=wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    """
    return structlog.get_logger(name)


# Create module-level logger
logger = get_logger(__name__)