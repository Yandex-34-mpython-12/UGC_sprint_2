from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.core.config import settings


def configure_tracer() -> None:
    tracer_provider = TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: settings.run.project_name,
                SERVICE_VERSION: settings.run.version,
            }
        ),
    )
    trace.set_tracer_provider(tracer_provider)
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger.agent_host_name,
        agent_port=settings.jaeger.agent_port,
    )
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    # Чтобы видеть трейсы в консоли
    # tracer_provider.add_span_processor(
    #     BatchSpanProcessor(ConsoleSpanExporter())
    # )
