"""OpenTelemetry tracing configuration for local and exported telemetry."""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


def configure_tracing() -> None:
    """Configure tracing once, using standard OTEL environment variables."""
    if isinstance(trace.get_tracer_provider(), TracerProvider):
        return

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": os.getenv(
                    "OTEL_SERVICE_NAME", "agentic-chaos-monkey"
                )
            }
        )
    )
    exporter = os.getenv("OTEL_TRACES_EXPORTER", "none").lower()
    if exporter == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    elif exporter == "otlp" or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

    trace.set_tracer_provider(provider)


def tracer(name: str = __name__) -> trace.Tracer:
    return trace.get_tracer(name)
