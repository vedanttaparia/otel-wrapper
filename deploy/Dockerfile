# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -u 1000 oteluser

# Set working directory
WORKDIR /app

# Ensure latest pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the package definitions and source folder
COPY pyproject.toml ./
COPY src/ ./src/

# Install the application as a native system package
RUN pip install --no-cache-dir .

# Switch to non-root user
USER oteluser

# This image serves as a generic runtime environment injected with dependencies.
# The entrypoint will be overwritten by Docker Swarm or Compose to execute the injected configuration scripts.
ENTRYPOINT ["python"]
CMD ["-m", "cli", "--help"]
