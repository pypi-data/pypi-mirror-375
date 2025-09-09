"""Configuration and initialization for OpenTelemetry logging."""

import logging
import os
from typing import Dict, Tuple

# OpenTelemetry Logs API is available in opentelemetry-sdk >= 1.27.0
from opentelemetry._logs import LoggerProvider
from opentelemetry._logs import get_logger as get_otel_logger
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider as SDKLoggerProvider
from opentelemetry.sdk._logs import LoggingHandler, LogRecordProcessor
from opentelemetry.sdk.resources import Resource
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter

logger = logging.getLogger(__name__)


# Simple concrete LogRecordProcessor implementation
class SimpleLogRecordProcessor(LogRecordProcessor):
    def __init__(self, exporter):
        self.exporter = exporter

    def emit(self, log_record):
        try:
            self.exporter.export([log_record])
        except Exception:
            pass  # Silently fail on export errors

    def force_flush(self, timeout_millis=30000):
        try:
            self.exporter.force_flush(timeout_millis)
        except Exception:
            pass

    def shutdown(self, timeout_millis=30000):
        try:
            self.exporter.shutdown(timeout_millis)
        except Exception:
            pass


def initialize_logging(
    endpoint: str,
    headers: Dict[str, str],
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
    *,
    replace_root_handlers: bool = False,
) -> Tuple[object, object]:
    """
    Initialize OpenTelemetry Logs and install a bridge handler on stdlib logging.

    Args:
        endpoint: OTLP endpoint for log export
        headers: Authentication headers for OTLP requests
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint: Whether the endpoint came from Bitwarden vault
        replace_root_handlers: If True, replace existing root handlers to avoid duplicates

    Returns:
        Tuple of (logger_provider, logging_handler)
    """

    try:
        provider = SDKLoggerProvider(resource=resource)

        # Create log exporter using centralized function with smart protocol detection
        exporter = build_otlp_exporter(
            TelemetryType.LOGGING, endpoint, headers, is_bitwarden_endpoint
        )
        processor = SimpleLogRecordProcessor(exporter)
        provider.add_log_record_processor(processor)

        set_logger_provider(provider)

        handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
        root_logger = logging.getLogger()
        if replace_root_handlers:
            root_logger.handlers = []
        root_logger.addHandler(handler)

        # Maintain existing root level unless env overrides
        level_name = os.environ.get("THOUGHTFUL_OTEL_LOG_LEVEL")
        if level_name:
            try:
                root_logger.setLevel(getattr(logging, level_name.upper()))
            except Exception:
                logger.warning("Invalid THOUGHTFUL_OTEL_LOG_LEVEL: %s", level_name)

        logger.info("OpenTelemetry logging initialized – OTLP endpoint configured")

        return (provider, handler)

    except Exception as exc:
        logger.error("Failed to initialize logging: %s", str(exc))
        raise ValueError(f"Logging initialization failed: {str(exc)}")
