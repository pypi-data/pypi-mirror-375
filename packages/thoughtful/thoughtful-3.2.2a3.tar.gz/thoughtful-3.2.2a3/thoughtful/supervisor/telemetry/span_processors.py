"""Custom span processors for automatic metric recording."""

import logging
from typing import Any, Optional
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span
from thoughtful.supervisor.telemetry.exclusions import get_excluded_endpoints
from thoughtful.supervisor.telemetry.meter_utils import get_current_meter
from thoughtful.supervisor.telemetry.metrics.counters import (
    record_external_service_call,
)
from thoughtful.supervisor.telemetry.metrics.histograms import (
    record_external_response_time,
)

logger = logging.getLogger(__name__)


class ExternalServiceCallSpanProcessor(SpanProcessor):
    """
    A span processor that automatically records external service calls as metrics.

    This processor monitors spans and automatically increments the external service
    calls counter when it detects outgoing HTTP/gRPC calls to external services.
    """

    def __init__(self):
        """Initialize the external service call span processor."""
        super().__init__()

    def on_start(self, span: Span, parent_context: Optional[Any] = None) -> None:
        """
        Called when a span is started.

        Args:
            span: The span that was started
            parent_context: The parent context
        """
        # We don't need to do anything on span start

    def on_end(self, span: Span) -> None:
        """
        Called when a span is ended.

        This is where we check if the span represents an external service call
        and record the appropriate metric.

        Args:
            span: The span that was ended
        """
        # Check if this is an external service call span
        if self._is_external_service_call(span):
            meter = get_current_meter()
            if meter:
                url_hostname = self._extract_service_name(span)
                method = self._extract_method(span)
                parent_step_id = self._extract_parent_step_id(span)

                # Record external service call counter with minimal exception scope
                try:
                    record_external_service_call(meter, url_hostname, method)
                except Exception as e:
                    logger.debug(
                        "Failed to record external service call counter: %s", str(e)
                    )

                # Record external response time histogram
                if (
                    hasattr(span, "start_time")
                    and hasattr(span, "end_time")
                    and span.start_time is not None
                    and span.end_time is not None
                ):
                    # Handle different time formats (datetime objects vs timestamps)
                    if hasattr(span.end_time, "total_seconds"):
                        # datetime objects
                        duration = span.end_time - span.start_time
                        response_time_ms = duration.total_seconds()
                    else:
                        # timestamp integers (nanoseconds)
                        duration_ns = span.end_time - span.start_time
                        response_time_ms = (
                            duration_ns / 1_000_000
                        )  # Convert nanoseconds to milliseconds

                    # Record response time with minimal exception scope
                    try:
                        record_external_response_time(
                            meter,
                            url_hostname,
                            method,
                            response_time_ms,
                            parent_step_id,
                        )
                        logger.debug(
                            "Recorded external response time: %s %s = %.2f ms",
                            method,
                            url_hostname,
                            response_time_ms,
                        )
                    except Exception as e:
                        logger.debug(
                            "Failed to record external response time: %s", str(e)
                        )

    def _is_external_service_call(self, span: Span) -> bool:
        """
        Determine if a span represents an external service call.

        Args:
            span: The span to check

        Returns:
            True if the span represents an external service call, False otherwise
        """
        # Check span attributes for external service call indicators
        attributes = span.attributes or {}

        # HTTP client calls
        if "http.method" in attributes and "http.url" in attributes:
            # Check if it's not a call to our own services
            url = attributes.get("http.url", "")
            if self._is_external_url(url):
                return True

        # gRPC client calls
        if "rpc.method" in attributes and "rpc.service" in attributes:
            # Check if it's not a call to our own services using centralized exclusions
            service = attributes.get("rpc.service", "")
            # Use the same exclusion logic as URLs
            excluded_endpoints = get_excluded_endpoints()
            is_external = True
            for domain in excluded_endpoints:
                if domain in service:
                    is_external = False
                    break
            if is_external:
                return True

        return False

    def _is_external_url(self, url: str) -> bool:
        """
        Check if a URL represents an external service call.

        Args:
            url: The URL to check

        Returns:
            True if the URL is external, False otherwise
        """
        if not url:
            return False

        # Get the list of excluded endpoints from centralized configuration
        excluded_endpoints = get_excluded_endpoints()

        # Check if the URL contains any excluded domains
        for domain in excluded_endpoints:
            if domain in url:
                return False

        # If it's not internal, consider it external
        return True

    def _extract_service_name(self, span: Span) -> str:
        """
        Extract the service name from a span.

        Args:
            span: The span to extract the service name from

        Returns:
            The service name
        """
        attributes = span.attributes or {}

        # For HTTP calls, extract from URL
        if "http.url" in attributes:
            url = attributes.get("http.url", "")
            try:
                parsed = urlparse(url)
                return parsed.hostname or "unknown"
            except Exception:
                return "unknown"

        # For gRPC calls, use the service name
        if "rpc.service" in attributes:
            return attributes.get("rpc.service", "unknown")

        return "unknown"

    def _extract_method(self, span: Span) -> str:
        """
        Extract the method from a span.

        Args:
            span: The span to extract the method from

        Returns:
            The method name
        """
        attributes = span.attributes or {}

        # For HTTP calls, use the HTTP method
        if "http.method" in attributes:
            return attributes.get("http.method", "unknown")

        # For gRPC calls, use the RPC method
        if "rpc.method" in attributes:
            return attributes.get("rpc.method", "unknown")

        return "unknown"

    def _extract_parent_step_id(self, span: Span) -> str:
        """
        Extract the parent step ID from a span by looking up the span hierarchy.

        Args:
            span: The span to extract the parent step ID from

        Returns:
            The parent step ID or "unknown" if not available
        """
        try:
            # Check current span attributes for step.id first
            attributes = span.attributes or {}
            if "step.id" in attributes:
                return attributes["step.id"]

            # For HTTP/gRPC spans, we need to look at the active span context
            # to find the step that initiated this external call

            # Get the current active span (which should be the step span)
            current_span = trace.get_current_span()
            if current_span and current_span != span:
                current_attributes = getattr(current_span, "attributes", {}) or {}
                if "step.id" in current_attributes:
                    return current_attributes["step.id"]

                # Check the span name as well
                current_span_name = getattr(current_span, "name", "")
                if current_span_name and not current_span_name.startswith("HTTP "):
                    return current_span_name

            # Fallback: try to extract from span name if it's not a generic HTTP span
            span_name = getattr(span, "name", "")
            if (
                span_name
                and not span_name.startswith("HTTP ")
                and not span_name.startswith("gRPC ")
            ):
                return span_name

            # Final fallback
            return "external_call"

        except Exception:
            logger.debug("Failed to extract parent step ID")

        return "unknown"

    def shutdown(self) -> None:
        """Shutdown the span processor."""
        # No cleanup needed for this processor

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending spans.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            True if flush was successful, False otherwise
        """
        # No pending spans to flush for this processor
        return True
