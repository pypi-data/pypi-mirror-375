"""Counter metrics utilities for OpenTelemetry."""

import logging
from typing import Any, Dict

from opentelemetry import metrics
from thoughtful.supervisor.telemetry.meter_utils import get_current_meter

logger = logging.getLogger(__name__)


def create_workflow_started_counter(meter: Any, workflow_name: str) -> None:
    """
    Create a counter for tracking workflow starts and record the workflow start.

    Args:
        meter: OpenTelemetry meter instance
        workflow_name: Name of the workflow being started
    """
    if not meter:
        logger.warning("No meter provided for workflow started counter")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        # Create the counter
        counter = meter.create_counter(
            name=f"thoughtful.{service_name}.workflow.started",
            description="Total number of workflows started",
            unit="1",
        )

        # Add to the counter
        counter.add(1, {"agent.name": workflow_name})
        logger.debug("Recorded workflow started: %s", workflow_name)

    except Exception as e:
        logger.error("Failed to create and record workflow started counter: %s", str(e))


def create_workflow_completed_counter(meter: Any, workflow_name: str) -> None:
    """
    Create a counter for tracking workflow completions and record the workflow completion.

    Args:
        meter: OpenTelemetry meter instance
        workflow_name: Name of the workflow being completed
    """
    if not meter:
        logger.warning("No meter provided for workflow completed counter")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        # Create the counter
        counter = meter.create_counter(
            name=f"thoughtful.{service_name}.workflow.completed",
            description="Total number of workflows completed",
            unit="1",
        )

        # Add to the counter
        counter.add(1, {"agent.name": service_name})
        logger.debug("Recorded workflow completed: %s", service_name)

    except Exception as e:
        logger.error(
            "Failed to create and record workflow completed counter: %s", str(e)
        )


def create_step_executed_counter(meter: Any, step_id: str) -> Any:
    """
    Create a counter for tracking step executions.

    Args:
        meter: OpenTelemetry meter instance
        step_id: ID of the step being executed

    Returns:
        Counter metric object or None if creation fails
    """
    if not meter:
        logger.warning("No meter provided for step executed counter")
        return None

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")

        return meter.create_counter(
            name=f"thoughtful.{service_name}.{step_id}.executions",
            description=f"Total number of executions for step {step_id}",
            unit="executions",
        )
    except Exception as e:
        logger.error("Failed to create step executed counter: %s", str(e))
        return None


def record_step_executed(step_id: str) -> None:
    """
    Record that a step has been executed.
    This function should be called when a step starts to track
    step execution occurrences. It automatically gets the current meter.

    Args:
        step_id: ID of the step being executed
    """
    meter = get_current_meter()
    if meter:
        counter = create_step_executed_counter(meter, step_id)
        if counter:
            counter.add(1)
            logger.debug("Recorded step execution: %s", step_id)


# Global error counter cache to prevent multiple creation
_error_counter_cache: Dict[str, Any] = {}


def create_errors_total_counter(
    meter: Any, step_id: str, error_type: str = "unknown"
) -> None:
    """
    Create or get a global counter for tracking errors encountered and record the error.

    Args:
        meter: OpenTelemetry meter instance
        step_id: ID of the step where the error occurred
        error_type: Type of error that occurred
    """
    if not meter:
        logger.warning("No meter provided for errors total counter")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        service_name = getattr(meter, "_name", "thoughtful-supervisor")
        counter_key = f"{service_name}.errors.total"

        # Get or create the global error counter
        if counter_key not in _error_counter_cache:
            _error_counter_cache[counter_key] = meter.create_counter(
                name=f"thoughtful.{service_name}.errors.total",
                description="Total number of errors encountered",
                unit="1",
            )

        # Add to the counter
        _error_counter_cache[counter_key].add(
            1, {"agent.name": step_id, "error.type": error_type}
        )
        logger.debug("Recorded error: step=%s, type=%s", step_id, error_type)

    except Exception as e:
        logger.error("Failed to create and record errors total counter: %s", str(e))


def create_external_service_calls_counter(
    meter: Any, service_name: str = "unknown", method: str = "unknown"
) -> None:
    """
    Create a counter for tracking external service calls and record the call.

    Args:
        meter: OpenTelemetry meter instance
        service_name: Name of the external service being called
        method: HTTP method or gRPC method being called
    """
    if not meter:
        logger.warning("No meter provided for external service calls counter")
        return

    try:
        # Get service name from meter name (meter._name contains the service name)
        meter_service_name = getattr(meter, "_name", "thoughtful-supervisor")

        # Create the counter
        counter = meter.create_counter(
            name=f"thoughtful.{meter_service_name}.agent.calls",
            description="Total number of external service calls made",
            unit="1",
        )

        # Add to the counter
        counter.add(1, {"agent.name": service_name, "method": method})
        logger.debug(
            "Recorded external service call: service=%s, method=%s",
            service_name,
            method,
        )

    except Exception as e:
        logger.error(
            "Failed to create and record external service calls counter: %s", str(e)
        )


def record_workflow_started(meter: Any, workflow_name: str) -> None:
    """
    Record that a workflow has started.

    This function should be called when the root span is created to track
    workflow initialization.

    Args:
        meter: OpenTelemetry meter instance
        workflow_name: Name of the workflow being started
    """
    create_workflow_started_counter(meter, workflow_name)


def record_workflow_completed(meter: Any, workflow_name: str) -> None:
    """
    Record that a workflow has completed.

    This function should be called when the root span is exiting to track
    workflow completion.

    Args:
        meter: OpenTelemetry meter instance
        workflow_name: Name of the workflow being completed
    """
    create_workflow_completed_counter(meter, workflow_name)


def record_step_error(step_id: str, error_type: str = "unknown") -> None:
    """
    Record that a step error has occurred.

    This function should be called when a step encounters an error to track
    error occurrences. It automatically gets the current meter.

    Args:
        step_id: ID of the step where the error occurred
        error_type: Type of error that occurred
    """

    meter = get_current_meter()
    if meter:
        create_errors_total_counter(meter, step_id, error_type)


def record_external_service_call(
    meter: Any, service_name: str = "unknown", method: str = "unknown"
) -> None:
    """
    Record that an external service call has been made.
    This function should be called when an external service call is made to track
    external service usage.
    Args:
        meter: OpenTelemetry meter instance
        service_name: Name of the external service being called
        method: HTTP method or gRPC method being called
    """
    create_external_service_calls_counter(meter, service_name, method)
