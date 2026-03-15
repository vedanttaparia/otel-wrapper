#!/bin/bash
# Example automation script to be injected via Docker Swarm Configs

echo "Starting Automation Script Emission..."

# Target the locally bound collector from the Verification Phase (or external swarm service)
ENDPOINT="http://otel-infra_otel-collector:4317"

# Expected to be inside the container (/app is WORKDIR)
echo "Emitting metric 1 (Counter)..."
python cli.py emit_counter --name "app.jobs.started" --value 10 --label "job_type=backup" --endpoint "$ENDPOINT"

echo "Emitting metric 2 (UpDownCounter)..."
python cli.py emit_up_down_counter --name "app.queue.size" --value -5 --label "queue=high_priority" --endpoint "$ENDPOINT"

echo "Emitting metric 3 (Histogram)..."
python cli.py emit_histogram --name "app.request.duration" --value 1.25 --label "endpoint=/api/v1/users" --endpoint "$ENDPOINT"

echo "Emitting metric 4 (Counter with multiple labels)..."
python cli.py emit_counter --name "app.login.failures" --value 1 --label "reason=invalid_password" --label "region=us-east" --endpoint "$ENDPOINT"

echo "Emitting metric 5 (Network Failure Test)..."
# This tests the constraint that a failure to connect won't crash the script
python cli.py emit_counter --name "app.db.errors" --value 1 --endpoint "http://invalid-endpoint:4317"

echo "Automation Script Finished successfully."
