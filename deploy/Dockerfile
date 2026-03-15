# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -u 1000 oteluser

# Set working directory
WORKDIR /app

# Ensure latest pip
RUN pip install --no-cache-dir --upgrade pip

# Install OpenTelemetry dependencies
RUN pip install --no-cache-dir \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-grpc

# Copy our robust, memory-safe library modules
COPY checker.py .
COPY otel_lib.py .
COPY cli.py .

# Switch to non-root user
USER oteluser

# This image serves as a generic runtime environment injected with dependencies.
# The entrypoint will be overwritten by Docker Swarm or Compose to execute the injected configuration scripts.
ENTRYPOINT ["python"]
CMD ["-m", "cli", "--help"]
