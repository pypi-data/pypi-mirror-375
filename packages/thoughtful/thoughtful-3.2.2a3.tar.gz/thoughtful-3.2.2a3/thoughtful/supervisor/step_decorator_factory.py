"""
This module contains the functions necessary to fuel the step decorator
factory function ``create_step_decorator``. This step decorator—``@step``—is
used to supervise the execution of a function in a digital worker.

.. code-block:: python

    from thoughtful.supervisor import supervise, step

    @step("1.1")
    def times_two(integers: list) -> None:
        return integers * 2

    @step("1.2")
    def times_three(integer: int) -> None:
        return integer * 3

    def main():
        num_list = [1, 2, 3, 4, 5]

        num_list = times_two(num_list)

        for num in num_list:
            num = times_three(num)

    if __name__ == '__main__':
        with supervise():
            main()

The decorator produced by the factory does not have any immediate support for
records, nor for setting the step status like the step context does. However,
some helpers have been implemented to simulate this functionality. For the
record IDs, the decorator will look for a function kwarg called
``supervisor_record_id`` and use that as the record ID.

.. code-block:: python

    @step("1.2")
    def times_three(integer: int, supervisor_record_id: str = None) -> None:
        return integer * 3

    num = times_three(3, supervisor_record_id=str(3))

As for the step status, a helper function, ``set_step_status``, has been
implemented to set the status of a step.

.. code-block:: python

    @step("1.1")
    def times_two(integers: list) -> None:
        return integers * 2

    num_list = [1, 2, 3, 4, 5]
    num_list = times_two(num_list)
    set_step_status("1.1", "warning")
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, Optional, ParamSpec, Protocol, TypeVar

from opentelemetry import trace
from opentelemetry.trace import Status as TraceStatus
from opentelemetry.trace import StatusCode
from thoughtful.supervisor.event_bus import EventBus, StepReportChangeEvent
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.reporting.report_builder import StepReportBuilder
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.timer import Timer
from thoughtful.supervisor.step_context import StepContext, StepLifecycleCallbackType
from thoughtful.supervisor.telemetry.meter_utils import get_current_meter
from thoughtful.supervisor.telemetry.metrics.counters import record_step_error
from thoughtful.supervisor.telemetry.metrics.counters import record_step_executed
from thoughtful.supervisor.telemetry.metrics.histograms import record_step_duration

logger = logging.getLogger(__name__)

DecoratedFunctionParams = ParamSpec("DecoratedFunctionParams")
DecoratedFunctionReturn = TypeVar("DecoratedFunctionReturn")

DecoratedFunction = Callable[DecoratedFunctionParams, DecoratedFunctionReturn]


class StepDecorator(Protocol):
    def __call__(
        self,
        step_id: str,
        on_step_enter_callback: Optional[StepLifecycleCallbackType] = None,
        on_step_exit_callback: Optional[StepLifecycleCallbackType] = None,
    ) -> DecoratedFunction:
        ...


def create_step_decorator(
    report_builder: ReportBuilder,
    event_bus: EventBus,
) -> StepDecorator:
    """
    A step decorator generator that as input receives a ``ReportBuilder``
    object and a ``Recorder`` object. The returned decorator will use these
    objects to record the execution of the decorated function.

    Args:
        report_builder (ReportBuilder): The report builder to use to record
            the execution of the decorated function.
        event_bus (EventBus): The decorator will emit events, such as when
            a step report has been created or updated, to this bus.

    Returns:
        StepDecorator: A decorator to attach to functions.
    """

    # The decorator to be returned as the property
    # This handles the inputs to the decorator itself
    def returned_decorator(
        step_id: str,
        on_step_enter_callback: Optional[StepLifecycleCallbackType] = None,
        on_step_exit_callback: Optional[StepLifecycleCallbackType] = None,
    ) -> DecoratedFunction:
        """
        A decorator to mark a function as the implementation of a step in a
        digital worker's manifest.

        To include a `supervisor_record_id`, pass it to the decorated function
        as a kwarg. For example,
        ```
            @step(1)
            def my_func(*args, supervisor_record_id: str):
                do stuff
                ...

            my_func(supervisor_record_id="my_record_id")
        ```
        """

        # The decorator to grab the function callable itself
        def inner_decorator(
            fn: DecoratedFunction[DecoratedFunctionParams, DecoratedFunctionReturn],
        ):
            # And the wrapper around the function to call it with its
            # args and kwargs arguments
            @functools.wraps(fn)
            def wrapper(
                *fn_args: DecoratedFunctionParams.args,
                **fn_kwargs: DecoratedFunctionParams.kwargs,
            ) -> DecoratedFunctionReturn:
                return _run_wrapped_func(
                    fn,
                    step_id,
                    report_builder,
                    event_bus,
                    on_step_enter_callback,
                    on_step_exit_callback,
                    *fn_args,
                    **fn_kwargs,
                )

            return wrapper

        return inner_decorator

    return returned_decorator


def _run_wrapped_func(
    fn: DecoratedFunction[DecoratedFunctionParams, DecoratedFunctionReturn],
    step_id: str,
    report_builder: ReportBuilder,
    event_bus: EventBus,
    on_step_enter_callback: Optional[StepLifecycleCallbackType] = None,
    on_step_exit_callback: Optional[StepLifecycleCallbackType] = None,
    *fn_args: DecoratedFunctionParams.args,
    **fn_kwargs: DecoratedFunctionParams.kwargs,
) -> DecoratedFunctionReturn:
    """
    Runs `fn` with the given args `args` and `kwargs`, times how long it
    takes to run, and records the execution of this function under `step_id`
    in the work report.

    Args:
        fn (DecoratedFunction[DecoratedFunctionParams, DecoratedFunctionReturn]): The function to run.
        step_id (str): The ID of the step representing the function to execute.
        report_builder (ReportBuilder): The ReportBuilder to add the function execution to.
        event_bus (EventBus): An event bus to manage step report changes.
        on_step_enter_callback (StepLifecycleCallbackType): Callback to be executed at the start.
        on_step_exit_callback (StepLifecycleCallbackType): Callback to be executed at the end.
        *args (DecoratedFunctionParams.args): The input arguments to the function.
        **kwargs (DecoratedFunctionParams.kwargs): The input keyword arguments to the function.

    Returns:
        DecoratedFunctionReturn: Whatever is returned by executing the function
    """

    """Set up the step"""
    caught_exception: Optional[Exception] = None
    final_status: Status

    step_cm = None
    step_span = None
    try:
        # Get the current root span from the trace context
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            tracer = trace.get_tracer(__name__)
            step_cm = tracer.start_as_current_span(
                name=f"step.{step_id}",
                attributes={"step.id": step_id},
                end_on_exit=False,
            )
            step_span = step_cm.__enter__()
    except Exception:
        # Tracing not configured or failed
        pass

    # Record step execution
    try:
        record_step_executed(step_id)
    except Exception as e:
        logger.debug("Failed to record step execution: %s", str(e))

    on_enter_callback = (
        on_step_enter_callback or StepContext.get_on_step_enter_callback()
    )
    on_exit_callback = on_step_exit_callback or StepContext.get_on_step_exit_callback()

    if on_enter_callback:
        try:
            on_enter_callback(step_id)
        except Exception as ex:
            logger.warning(f"Error in on_enter_callback for step {step_id}: {ex}")

    # Time the function
    func_timer = Timer()
    func_timer.start()

    this_steps_report_builder = StepReportBuilder(
        step_id=step_id,
        start_time=func_timer.start_time,
        end_time=None,
        status=Status.RUNNING,
    )

    for report in this_steps_report_builder.to_reports():
        new_event = StepReportChangeEvent(step_report=report)
        event_bus.emit(new_event)

    """Run the step"""
    fn_result: Any = None
    try:
        fn_result = fn(*fn_args, **fn_kwargs)
        final_status = Status.SUCCEEDED
    except Exception as ex:
        caught_exception = ex
        final_status = Status.FAILED
    timer_result = func_timer.end()

    # Finish the report
    this_steps_report_builder.end_time = timer_result.end
    this_steps_report_builder.status = final_status

    report_builder.add_step_report(this_steps_report_builder)
    for report in this_steps_report_builder.to_reports():
        new_event = StepReportChangeEvent(step_report=report)
        event_bus.emit(new_event)

    if on_exit_callback:
        try:
            on_exit_callback(step_id)
        except Exception as ex:
            logger.warning(f"Error in on_exit_callback for step {step_id}: {ex}")

    # Close the span if it was created
    if step_span is not None:
        if caught_exception:
            step_span.set_status(TraceStatus(StatusCode.ERROR))
            step_span.record_exception(caught_exception)

            # Record error metric
            try:
                error_type = caught_exception.__class__.__name__
                record_step_error(step_id, error_type)
            except Exception as metric_error:
                logger.warning(
                    f"Failed to record error metric for step {step_id}: {metric_error}"
                )
        else:
            step_span.set_status(TraceStatus(StatusCode.OK))

        step_span.end()

        # Record step duration from the closed span
        meter = get_current_meter()
        if meter and (
            hasattr(step_span, "start_time")
            and hasattr(step_span, "end_time")
            and step_span.start_time is not None
            and step_span.end_time is not None
        ):
            # Handle different time formats (datetime objects vs timestamps)
            if hasattr(step_span.end_time, "total_seconds"):
                # datetime objects
                duration = step_span.end_time - step_span.start_time
                duration_ms = (
                    duration.total_seconds() * 1000
                )  # Convert seconds to milliseconds
            else:
                # timestamp integers (nanoseconds)
                duration_ns = step_span.end_time - step_span.start_time
                duration_ms = (
                    duration_ns / 1_000_000
                )  # Convert nanoseconds to milliseconds

            # Record duration with minimal exception scope
            try:
                record_step_duration(meter, step_id, duration_ms)
                logger.debug(
                    "Recorded step duration: %s = %.2f ms", step_id, duration_ms
                )
            except Exception as duration_error:
                logger.warning(
                    f"Failed to record step duration for {step_id}: {duration_error}"
                )

        step_cm.__exit__(
            caught_exception.__class__ if caught_exception else None,
            caught_exception,
            None,
        )

    """Passthrough the step's return value or raised exception"""
    # If the step failed and raised an exception, raise that instead
    # of returning None
    if caught_exception:
        raise caught_exception

    # Passthrough the function's returned data back up
    return fn_result
