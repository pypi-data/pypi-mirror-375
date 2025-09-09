"""Histogram metrics utilities for OpenTelemetry."""

import logging
from typing import Any

from opentelemetry import metrics

logger = logging.getLogger(__name__)


def create_workflow_duration_histogram(meter: Any) -> Any:
    """
    Create a histogram for tracking workflow duration.

    Args:
        meter: OpenTelemetry meter instance

    Returns:
        Histogram metric object or None if creation fails
    """
    if not meter:
        logger.warning("No meter provided for workflow duration histogram")
        return None

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        return meter.create_histogram(
            name=f"thoughtful.{service_name}.workflow.duration",
            description="Duration of workflow execution in milliseconds",
            unit="ms",
        )
    except Exception as e:
        logger.error("Failed to create workflow duration histogram: %s", str(e))
        return None


def create_external_response_time_histogram(meter: Any) -> Any:
    """
    Create a histogram for tracking external service response times.

    Args:
        meter: OpenTelemetry meter instance

    Returns:
        Histogram metric object or None if creation fails
    """
    if not meter:
        logger.warning("No meter provided for external response time histogram")
        return None

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        return meter.create_histogram(
            name=f"thoughtful.{service_name}.external.response_time",
            description="Response time of external service calls in milliseconds",
            unit="ms",
        )
    except Exception as e:
        logger.error("Failed to create external response time histogram: %s", str(e))
        return None


def record_workflow_duration(
    meter: Any, workflow_name: str, duration_ms: float
) -> None:
    """
    Record workflow duration in the histogram.

    Args:
        meter: OpenTelemetry meter instance
        workflow_name: Name of the workflow
        duration_ms: Duration in milliseconds
    """
    if not meter:
        logger.warning("No meter provided for recording workflow duration")
        return

    try:
        histogram = create_workflow_duration_histogram(meter)
        if histogram:
            histogram.record(duration_ms, {"agent.name": workflow_name})
            logger.debug(
                "Recorded workflow duration: %s = %.2f ms", workflow_name, duration_ms
            )
    except Exception as e:
        logger.error("Failed to record workflow duration: %s", str(e))


def record_step_duration(meter: Any, step_id: str, duration_ms: float) -> None:
    """
    Record step duration in a service-specific histogram.

    Args:
        meter: OpenTelemetry meter instance
        step_id: ID of the step
        duration_ms: Duration in milliseconds
    """
    if not meter:
        logger.warning("No meter provided for recording step duration")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        # Create a service and step-specific histogram
        histogram = meter.create_histogram(
            name=f"thoughtful.{service_name}.{step_id}.duration",
            description=f"Duration of step {step_id} execution in milliseconds",
            unit="ms",
        )

        if histogram:
            histogram.record(duration_ms)
            logger.debug(
                "Recorded step duration: %s.%s = %.2f ms",
                service_name,
                step_id,
                duration_ms,
            )
    except Exception as e:
        logger.error("Failed to record step duration: %s", str(e))


def record_external_response_time(
    meter: Any,
    url_hostname: str,
    method: str,
    response_time_ms: float,
    parent_step_id: str = "unknown",
) -> None:
    """
    Record external service response time in a service-specific histogram.

    Args:
        meter: OpenTelemetry meter instance
        url_hostname: Name of the external service
        method: HTTP method or gRPC method
        response_time_ms: Response time in milliseconds
        parent_step_id: ID of the parent step
    """
    if not meter:
        logger.warning("No meter provided for recording external response time")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        meter_service_name = getattr(meter, "_name", "thoughtful-supervisor")

        # Create a service, hostname, method, and parent step-specific histogram
        histogram = meter.create_histogram(
            name=f"thoughtful.{meter_service_name}.{url_hostname}.{method}.{parent_step_id}.duration",
            description=f"Response time of {method} requests to {url_hostname} from step {parent_step_id} in milliseconds",
            unit="ms",
        )

        if histogram:
            histogram.record(response_time_ms)
            logger.debug(
                "Recorded external response time: %s.%s.%s.%s = %.2f ms",
                meter_service_name,
                url_hostname,
                method,
                parent_step_id,
                response_time_ms,
            )
    except Exception as e:
        logger.error("Failed to record external response time: %s", str(e))
