import os
from opentelemetry import (
    trace
)
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.semconv.resource import ResourceAttributes

from grpc import ssl_channel_credentials
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

# Set up tracing
service_name = os.getenv("OTEL_SERVICE_NAME", "peterb-sequence-of-numbers")
resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: service_name
})
trace.set_tracer_provider(TracerProvider(resource=resource))

apikey = os.environ.get("HONEYCOMB_API_KEY", "missing API key")

# Send the traces to Honeycomb
hnyExporter = OTLPSpanExporter(
    endpoint="api.honeycomb.io:443",
   insecure=False,
    credentials=ssl_channel_credentials(),
    headers=(
        ("x-honeycomb-team", apikey),
    )
)

aspecto_auth = os.environ.get("ASPECTO_KEY", "missing Aspecto key")
aspecto_endpoint = os.environ.get("ASPECTO_ENDPOINT", "missing Aspecto endpoint")

print("Sending to " + aspecto_endpoint)
print("Authorization " + aspecto_auth)
aspecto_exporter = OTLPSpanExporter(
    endpoint=aspecto_endpoint,
    insecure=False,
    headers={"authorization": aspecto_auth}
)

jaeger_endpoint = os.environ.get("JAEGER_ENDPOINT")
jaegerExporter = OTLPSpanExporter(
    endpoint=jaeger_endpoint
)

#trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaegerExporter))
#trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(aspecto_exporter))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(hnyExporter))



# To see spans in the log, uncomment this:
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# auto-instrument outgoing requests
RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
