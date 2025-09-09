"""Core tracing configuration and initialization."""

import logging
from typing import Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter
from thoughtful.supervisor.telemetry.span_processors import (
    ExternalServiceCallSpanProcessor,
)
from thoughtful.supervisor.telemetry.tracing.instrumentation import (
    initialize_grpc_instrumentation,
)
from thoughtful.supervisor.telemetry.tracing.instrumentation import (
    initialize_http_instrumentation,
)

logger = logging.getLogger(__name__)


def initialize_tracing(
    *,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    enable_console_export: bool = False,
    enable_http_instrumentation: bool = True,
    enable_grpc_instrumentation: bool = True,
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
) -> None:
    """Configure a global :class:`TracerProvider`.

    Args:
        endpoint (str): The OTLP endpoint URL.
        headers (Dict[str, str], optional): Headers to include in OTLP requests.
        enable_console_export (bool): Whether to also export spans to console.
        enable_http_instrumentation (bool): Whether to automatically instrument HTTP libraries.
        enable_grpc_instrumentation (bool): Whether to automatically instrument gRPC.
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint (bool): Whether the endpoint came from Bitwarden vault

    Raises:
        ValueError: If the endpoint URL is invalid or unreachable.
    """
    # Basic validation - just ensure it's a non-empty string
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("OTLP endpoint must be a non-empty string")

    try:
        provider = TracerProvider(resource=resource)

        # Create exporter using centralized function with smart protocol detection
        exporter = build_otlp_exporter(
            TelemetryType.TRACING, endpoint, headers or {}, is_bitwarden_endpoint
        )

        provider.add_span_processor(BatchSpanProcessor(exporter))

        # Add custom span processor for external service call metrics
        provider.add_span_processor(ExternalServiceCallSpanProcessor())

        if enable_console_export:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry tracing initialized – OTLP endpoint configured")

        if enable_http_instrumentation:
            initialize_http_instrumentation()

        if enable_grpc_instrumentation:
            initialize_grpc_instrumentation()

    except Exception:
        logger.error("Failed to initialize OpenTelemetry tracing")
        raise ValueError("Failed to initialize tracing")
