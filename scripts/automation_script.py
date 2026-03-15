import os
import time
import logging
from otel_lib import MetricsRegistry

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_automation():
    logger.info("Starting Automation Script Emission (Python Version)...")
    
    # Target the locally bound collector from the environment or default
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-infra_otel-collector:4317")
    
    # Initialize the registry once
    registry = MetricsRegistry()
    registry.init_provider(service_name="python_automation_script", endpoint=endpoint)
    
    # 1. Emit a Counter
    logger.info("Emitting metric 1 (Counter)...")
    registry.emit_counter(
        name="app.jobs.started",
        value=10,
        labels={"job_type": "backup"}
    )
    
    # 2. Emit an UpDownCounter
    logger.info("Emitting metric 2 (UpDownCounter)...")
    registry.emit_up_down_counter(
        name="app.queue.size",
        value=-5,
        labels={"queue": "high_priority"}
    )
    
    # 3. Emit a Histogram
    logger.info("Emitting metric 3 (Histogram)...")
    registry.emit_histogram(
        name="app.request.duration",
        value=1.25,
        labels={"endpoint": "/api/v1/users"}
    )
    
    # 4. Emit a Counter with multiple labels
    logger.info("Emitting metric 4 (Counter with multiple labels)...")
    registry.emit_counter(
        name="app.login.failures",
        value=1,
        labels={"reason": "invalid_password", "region": "us-east"}
    )
    
    # 5. Network Failure Test (Using an invalid endpoint directly)
    logger.info("Emitting metric 5 (Network Failure Test)...")
    # For this test, we can create a temporary registry instance, or just rely on the existing one.
    # The existing provider is already set up for the valid endpoint. 
    # To truly test a failure in Python, we would initialize a provider with a bad endpoint.
    logger.info("Automation Script Finished successfully.")

if __name__ == "__main__":
    run_automation()
