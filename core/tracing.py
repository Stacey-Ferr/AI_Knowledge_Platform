from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

def setup_tracing():
    resource = Resource.create({
        "service.name" : "ai-knowledge-platform",
        "service.version" : "1.0.0",
        "deployment.environment" : "development"
    })

    provider = TracerProvider(resource=resource)

    provider.add_span_processor(
                                    BatchSpanProcessor(ConsoleSpanExporter())
                                )

    trace.set_tracer_provider(provider)