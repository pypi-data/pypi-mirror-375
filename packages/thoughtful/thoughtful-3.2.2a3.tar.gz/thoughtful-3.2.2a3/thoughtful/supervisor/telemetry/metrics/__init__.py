"""OpenTelemetry metrics utilities for Thoughtful supervisor."""

from thoughtful.supervisor.telemetry.metrics.config import initialize_metrics
from thoughtful.supervisor.telemetry.metrics.counters import create_errors_total_counter
from thoughtful.supervisor.telemetry.metrics.counters import (
    create_external_service_calls_counter,
)
from thoughtful.supervisor.telemetry.metrics.counters import (
    create_step_executed_counter,
)
from thoughtful.supervisor.telemetry.metrics.counters import (
    create_workflow_completed_counter,
)
from thoughtful.supervisor.telemetry.metrics.counters import (
    create_workflow_started_counter,
)
from thoughtful.supervisor.telemetry.metrics.counters import (
    record_external_service_call,
)
from thoughtful.supervisor.telemetry.metrics.counters import record_step_error
from thoughtful.supervisor.telemetry.metrics.counters import record_step_executed
from thoughtful.supervisor.telemetry.metrics.counters import record_workflow_started
from thoughtful.supervisor.telemetry.metrics.histograms import (
    create_external_response_time_histogram,
)
from thoughtful.supervisor.telemetry.metrics.histograms import (
    create_workflow_duration_histogram,
)
from thoughtful.supervisor.telemetry.metrics.histograms import (
    record_external_response_time,
)
from thoughtful.supervisor.telemetry.metrics.histograms import record_step_duration
from thoughtful.supervisor.telemetry.metrics.histograms import record_workflow_duration

__all__ = [
    "initialize_metrics",
    "create_workflow_duration_histogram",
    "create_external_response_time_histogram",
    "create_workflow_started_counter",
    "create_workflow_completed_counter",
    "create_step_executed_counter",
    "create_errors_total_counter",
    "create_external_service_calls_counter",
    "record_step_error",
    "record_step_executed",
    "record_workflow_started",
    "record_workflow_duration",
    "record_step_duration",
    "record_external_response_time",
    "record_external_service_call",
]
