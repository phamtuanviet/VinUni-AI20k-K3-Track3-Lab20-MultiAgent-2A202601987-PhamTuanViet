"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    import os
    use_langsmith = os.getenv("LANGCHAIN_TRACING_V2") == "true"
    
    if use_langsmith:
        try:
            from langsmith import trace
            with trace(name=name, inputs=attributes or {}):
                try:
                    yield span
                finally:
                    span["duration_seconds"] = perf_counter() - started
            return
        except ImportError:
            pass
            
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
