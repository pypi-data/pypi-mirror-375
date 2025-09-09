"""Centralized telemetry configuration and setup."""

import logging
import os
import platform
import socket
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, Optional, Type

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import (
    ResourceAttributes as SemConvResourceAttributes,
)
from thoughtful.supervisor.telemetry.common import TelemetryType, get_vault_otlp_config
from thoughtful.supervisor.telemetry.common import resolve_auth_headers
from thoughtful.supervisor.telemetry.common import resolve_shared_endpoint
from thoughtful.supervisor.telemetry.logging.config import initialize_logging
from thoughtful.supervisor.telemetry.meter_utils import set_current_service_name
from thoughtful.supervisor.telemetry.metrics.config import initialize_metrics
from thoughtful.supervisor.telemetry.metrics.counters import record_workflow_completed
from thoughtful.supervisor.telemetry.metrics.counters import record_workflow_started
from thoughtful.supervisor.telemetry.metrics.histograms import record_workflow_duration
from thoughtful.supervisor.telemetry.tracing import close_root_span
from thoughtful.supervisor.telemetry.tracing.config import initialize_tracing
from thoughtful.supervisor.telemetry.tracing.spans import create_root_span
from thoughtful.supervisor.telemetry.tracing.workflow import analyze_workflow_structure

logger = logging.getLogger(__name__)


# Global telemetry state management
_global_telemetry_context: Optional["TelemetryContext"] = None


def get_global_telemetry_context() -> Optional["TelemetryContext"]:
    """
    Get the global telemetry context if it exists.

    Returns:
        The global TelemetryContext or None if not initialized
    """
    return _global_telemetry_context


def set_global_telemetry_context(context: "TelemetryContext") -> None:
    """
    Set the global telemetry context.

    Args:
        context: The TelemetryContext to set as global
    """
    global _global_telemetry_context
    _global_telemetry_context = context


def clear_global_telemetry_context() -> None:
    """Clear the global telemetry context."""
    global _global_telemetry_context
    _global_telemetry_context = None


@dataclass
class TelemetryConfig:
    """Centralized configuration for all telemetry components."""

    # Service identification
    service_name: str
    manifest: Optional[Any] = None

    # Shared OTLP endpoint for all telemetry types
    endpoint: Optional[str] = None
    is_bitwarden_endpoint: bool = False

    # Authentication headers for OTLP requests
    auth_headers: Optional[Dict[str, str]] = None

    # Feature toggles to enable/disable telemetry components
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True

    # Custom resource attributes to add to all telemetry data
    resource_attributes: Optional[Dict[str, Any]] = None


@dataclass
class TelemetryContext:
    """Context object holding initialized telemetry components."""

    # Core components
    root_span_cm: Optional[Any] = None
    root_span: Optional[Any] = None
    meter_provider: Optional[Any] = None
    meter: Optional[Any] = None

    # Configuration used
    config: Optional[TelemetryConfig] = None

    # Resource built for all components
    resource: Optional[Resource] = None


class TelemetryConfigBuilder:
    """Builder for creating TelemetryConfig with proper defaults and validation."""

    def __init__(self):
        self._config = TelemetryConfig(service_name="")

    def with_service_name(self, name: str) -> "TelemetryConfigBuilder":
        """Set the service name."""
        self._config.service_name = name
        return self

    def with_manifest(self, manifest: Any) -> "TelemetryConfigBuilder":
        """Set the manifest object."""
        self._config.manifest = manifest
        return self

    def with_otlp_config(
        self, otlp_config: Optional[Dict[str, Any]]
    ) -> "TelemetryConfigBuilder":
        """Resolve all endpoints and auth from OTLP config, with automatic Bitwarden fallback."""
        # If no explicit config provided, try to use Bitwarden configuration
        if not otlp_config:
            try:
                vault_config = get_vault_otlp_config()
                if vault_config:
                    otlp_config = vault_config
                    logger.debug("Using Bitwarden configuration for telemetry")
                else:
                    logger.debug("No Bitwarden configuration found, using defaults")
            except Exception as e:
                logger.debug("Failed to get Bitwarden configuration: %s", str(e))

        if not otlp_config:
            return self

        # Resolve shared endpoint for all telemetry types (only once)
        (
            self._config.endpoint,
            self._config.is_bitwarden_endpoint,
        ) = resolve_shared_endpoint(otlp_config)

        # Resolve authentication headers
        try:
            self._config.auth_headers = resolve_auth_headers(otlp_config)
        except Exception as e:
            logger.error("Failed to resolve telemetry authentication: %s", str(e))
            self._config.auth_headers = {}

        return self

    def with_feature_toggles(self, **toggles) -> "TelemetryConfigBuilder":
        """Set feature toggles."""
        for key, value in toggles.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        return self

    def build(self) -> TelemetryConfig:
        """Build and validate the configuration."""
        self._validate()
        return self._config

    def _validate(self) -> None:
        """Validate the configuration."""
        if not self._config.service_name:
            raise ValueError("Service name is required")

        # Extract service name from manifest if available
        if (
            self._config.manifest
            and hasattr(self._config.manifest, "name")
            and self._config.manifest.name
        ):
            self._config.service_name = self._config.manifest.name


def extract_machine_attributes() -> Dict[str, Any]:
    """
    Extract machine attributes that are certainly available.
    Focuses on OS-level information and container details.

    Returns:
        Dictionary of machine attributes following OpenTelemetry semantic conventions
    """
    attributes = {}

    attributes[SemConvResourceAttributes.HOST_NAME] = socket.gethostname()
    attributes[SemConvResourceAttributes.HOST_ARCH] = platform.machine()
    attributes[SemConvResourceAttributes.OS_TYPE] = platform.system()
    attributes[SemConvResourceAttributes.OS_VERSION] = platform.version()

    attributes[SemConvResourceAttributes.PROCESS_RUNTIME_NAME] = "python"
    attributes[
        SemConvResourceAttributes.PROCESS_RUNTIME_VERSION
    ] = platform.python_version()

    attributes[SemConvResourceAttributes.DEPLOYMENT_ENVIRONMENT] = (
        "production" if os.environ.get("THOUGHTFUL_PRODUCTION") else "development"
    )

    if os.environ.get("CONTAINER_ID"):
        attributes[SemConvResourceAttributes.CONTAINER_ID] = os.environ.get(
            "CONTAINER_ID"
        )

    if os.environ.get("IMAGE_NAME"):
        attributes[SemConvResourceAttributes.CONTAINER_IMAGE_NAME] = os.environ.get(
            "IMAGE_NAME"
        )
        attributes[SemConvResourceAttributes.CONTAINER_IMAGE_TAG] = os.environ.get(
            "IMAGE_TAG", "latest"
        )
    return attributes


def extract_workflow_metrics(manifest) -> Dict[str, Any]:
    """
    Extract workflow metrics from manifest data that are certainly available.

    Args:
        manifest: The manifest object containing workflow information

    Returns:
        Dictionary of metrics that can be used as span attributes
    """
    if not manifest:
        return {}

    metrics = {}

    # Basic manifest information
    metrics["thoughtful.manifest.uid"] = manifest.uid
    metrics["thoughtful.manifest.name"] = manifest.name
    metrics["thoughtful.manifest.description"] = manifest.description or "unknown"
    metrics["thoughtful.manifest.author"] = manifest.author or "unknown"
    metrics["thoughtful.manifest.source"] = manifest.source

    # Workflow structure metrics
    workflow_stats = analyze_workflow_structure(manifest.workflow)
    metrics.update(workflow_stats)

    return metrics


def _build_resource_from_config(config: TelemetryConfig) -> Resource:
    """
    Build a shared resource with machine and workflow attributes.

    This resource will be used across all telemetry components to ensure
    consistent attribute collection and avoid duplication.

    Args:
        config: TelemetryConfig containing service name and manifest

    Returns:
        OpenTelemetry Resource with all attributes
    """
    machine_attributes = extract_machine_attributes()
    workflow_metrics = extract_workflow_metrics(config.manifest)

    attributes: Dict[str, Any] = {
        "service.name": config.service_name,
        **machine_attributes,
        **workflow_metrics,
    }

    # Add any custom resource attributes from config
    if config.resource_attributes:
        attributes.update(config.resource_attributes)

    return Resource.create(attributes)


def setup_telemetry_from_config(config: TelemetryConfig) -> TelemetryContext:
    """
    Consolidated setup function using TelemetryConfig.

    This is the internal implementation used by the public setup_telemetry function.
    It provides a more maintainable and testable approach to telemetry initialization.

    Args:
        config: TelemetryConfig containing all telemetry configuration

    Returns:
        TelemetryContext with initialized components
    """
    # Set the global service name for meter retrieval
    set_current_service_name(config.service_name)

    # Build shared resource for all telemetry components
    resource = _build_resource_from_config(config)

    # Initialize context
    context = TelemetryContext(config=config, resource=resource)

    # Initialize components with fail-open approach
    if config.enable_tracing and config.endpoint:
        try:
            initialize_tracing(
                endpoint=config.endpoint,
                headers=config.auth_headers or {},
                resource=resource,
                is_bitwarden_endpoint=config.is_bitwarden_endpoint,
            )

            # Create root span using the actual service name
            context.root_span_cm, context.root_span = create_root_span(
                config.service_name
            )

            logger.debug("OpenTelemetry tracing initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry tracing: %s", str(e))
            # Continue without tracing

    if config.enable_logging and config.endpoint:
        try:
            initialize_logging(
                endpoint=config.endpoint,
                headers=config.auth_headers or {},
                resource=resource,
                is_bitwarden_endpoint=config.is_bitwarden_endpoint,
            )

            logger.debug("OpenTelemetry logging initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry logging: %s", str(e))
            # Continue without logging

    if config.enable_metrics and config.endpoint:
        try:
            context.meter_provider, context.meter = initialize_metrics(
                endpoint=config.endpoint,
                headers=config.auth_headers or {},
                resource=resource,
                is_bitwarden_endpoint=config.is_bitwarden_endpoint,
            )

            logger.debug("OpenTelemetry metrics initialized successfully")

            # Record workflow started metric if both meter and root span were created successfully
            if context.meter and context.root_span:
                try:
                    record_workflow_started(context.meter, config.service_name)
                    logger.debug(
                        "Recorded workflow started metric for: %s", config.service_name
                    )
                except Exception as metric_error:
                    logger.error(
                        "Failed to record workflow started metric: %s",
                        str(metric_error),
                    )
                    # Continue without workflow started metric

        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry metrics: %s", str(e))
            # Continue without metrics

    # Set as global context for easy access
    set_global_telemetry_context(context)

    logger.info("Telemetry initialization completed")
    return context


def shutdown_telemetry_from_context(
    context: TelemetryContext,
    exc_type: Optional[Type[Exception]] = None,
    exc_val: Optional[Exception] = None,
    exc_tb: Optional[TracebackType] = None,
) -> None:
    """
    Shutdown telemetry components and record workflow completion.

    Args:
        context: TelemetryContext containing all telemetry components
        exc_type: Exception type if any
        exc_val: Exception value if any
        exc_tb: Exception traceback if any
    """
    if not context.config:
        return

    # Record workflow completion metric before closing the root span
    if context.meter is not None and context.config.manifest is not None:
        try:
            workflow_name = getattr(
                context.config.manifest, "name", "thoughtful-supervisor"
            )
            record_workflow_completed(context.meter, workflow_name)
            logger.debug("Recorded workflow completed metric for: %s", workflow_name)
        except Exception as metric_error:
            logger.error(
                "Failed to record workflow completed metric: %s", str(metric_error)
            )
            # Continue without workflow completed metric

    # Clean up the root tracing span if it was started
    if context.root_span_cm is not None and context.root_span is not None:
        close_root_span(
            context.root_span_cm, context.root_span, exc_type, exc_val, exc_tb
        )

        # Record workflow duration from the closed span
        if context.meter is not None and context.config.manifest is not None:
            workflow_name = getattr(
                context.config.manifest, "name", "thoughtful-supervisor"
            )

            # Get duration from the closed span
            if (
                hasattr(context.root_span, "start_time")
                and hasattr(context.root_span, "end_time")
                and context.root_span.start_time is not None
                and context.root_span.end_time is not None
            ):
                # Handle different time formats (datetime objects vs timestamps)
                if hasattr(context.root_span.end_time, "total_seconds"):
                    # datetime objects
                    duration = context.root_span.end_time - context.root_span.start_time
                    duration_ms = (
                        duration.total_seconds() * 1000
                    )  # Convert seconds to milliseconds
                else:
                    # timestamp integers (nanoseconds)
                    duration_ns = (
                        context.root_span.end_time - context.root_span.start_time
                    )
                    duration_ms = (
                        duration_ns / 1_000_000
                    )  # Convert nanoseconds to milliseconds

                # Record duration with minimal exception scope
                try:
                    record_workflow_duration(context.meter, workflow_name, duration_ms)
                    logger.debug(
                        "Recorded workflow duration for: %s = %.2f ms",
                        workflow_name,
                        duration_ms,
                    )
                except Exception as duration_error:
                    logger.error(
                        "Failed to record workflow duration: %s", str(duration_error)
                    )
                    # Continue without workflow duration metric

    # Clean up metrics if they were initialized
    if context.meter_provider is not None:
        try:
            context.meter_provider.shutdown()
        except Exception:
            logger.exception("Failed to shutdown meter provider")

    # Clear global context
    clear_global_telemetry_context()


# Main API functions
def setup_telemetry(
    otlp_config: Optional[Dict[str, Any]] = None,
    manifest: Any = None,
    service_name: str = "thoughtful-supervisor",
) -> TelemetryContext:
    """
    Initialize all OpenTelemetry telemetry components using TelemetryConfig.

    Args:
        otlp_config: Optional dictionary containing OTLP configuration
        manifest: Optional manifest object for resource attributes and service name
        service_name: Name of the service for resource attributes

    Returns:
        TelemetryContext with initialized components
    """
    config = (
        TelemetryConfigBuilder()
        .with_service_name(service_name)
        .with_manifest(manifest)
        .with_otlp_config(otlp_config)
        .build()
    )

    return setup_telemetry_from_config(config)


def shutdown_telemetry(
    context: TelemetryContext,
    exc_type: Optional[Type[Exception]] = None,
    exc_val: Optional[Exception] = None,
    exc_tb: Optional[TracebackType] = None,
) -> None:
    """
    Shutdown telemetry components and record workflow completion.

    Args:
        context: TelemetryContext containing all telemetry components
        exc_type: Exception type if any
        exc_val: Exception value if any
        exc_tb: Exception traceback if any
    """
    shutdown_telemetry_from_context(context, exc_type, exc_val, exc_tb)


# Convenience functions for accessing telemetry components
def get_current_meter():
    """
    Get the current meter from the global telemetry context.

    Returns:
        The current meter instance or None if not available
    """
    context = get_global_telemetry_context()
    return context.meter if context else None


def get_current_root_span():
    """
    Get the current root span from the global telemetry context.

    Returns:
        The current root span instance or None if not available
    """
    context = get_global_telemetry_context()
    return context.root_span if context else None


def is_telemetry_initialized() -> bool:
    """
    Check if telemetry is currently initialized.

    Returns:
        True if telemetry is initialized, False otherwise
    """
    return get_global_telemetry_context() is not None


def get_telemetry_config() -> Optional[TelemetryConfig]:
    """
    Get the current telemetry configuration.

    Returns:
        The current TelemetryConfig or None if not initialized
    """
    context = get_global_telemetry_context()
    return context.config if context else None
