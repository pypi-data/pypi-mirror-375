"""Configuration and initialization for OpenTelemetry metrics."""

import logging
from typing import Any, Dict

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter

logger = logging.getLogger(__name__)


def initialize_metrics(
    endpoint: str,
    headers: Dict[str, str],
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
) -> tuple[Any, Any]:
    """
    Initialize OpenTelemetry metrics with OTLP exporter using centralized configuration.

    Args:
        endpoint: OTLP endpoint for metrics export
        headers: Authentication headers for OTLP requests
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint: Whether the endpoint came from Bitwarden vault

    Returns:
        Tuple of (meter_provider, meter)

    Raises:
        ValueError: If metrics initialization fails
    """
    if resource is None:
        raise ValueError("Resource is required for metrics initialization")

    try:
        # Create metric exporter using centralized function with smart protocol detection
        exporter = build_otlp_exporter(
            TelemetryType.METRICS, endpoint, headers, is_bitwarden_endpoint
        )

        # Create metric reader with periodic export
        reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=10000,  # Export every 10 seconds
            export_timeout_millis=5000,  # 5 second timeout
        )

        # Create meter provider
        meter_provider = MeterProvider(
            metric_readers=[reader],
            resource=resource,
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        # Get meter for the service from the resource
        service_name = resource.attributes.get("service.name", "thoughtful-supervisor")
        meter = meter_provider.get_meter(service_name)

        logger.info(
            "OpenTelemetry metrics initialized successfully with endpoint: %s", endpoint
        )

        return meter_provider, meter

    except Exception as e:
        logger.error("Failed to initialize metrics: %s", str(e))
        raise ValueError(f"Metrics initialization failed: {str(e)}")
