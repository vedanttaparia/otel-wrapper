# 🔭 OpenTelemetry Python Wrapper & Swarm Stack

A memory-safe, lightweight Python wrapper for OpenTelemetry (OTel) metrics, pre-configured with a production-ready Docker Swarm observability stack (Prometheus & Grafana) featuring TLS-encrypted scraping.

---

## 🏗 Project Architecture

This project is separated into clean, modular tiers so that the application logic and observability infrastructure have independent lifecycles. 

```text
otel-wrapper/
├── src/            # Core Python OpenTelemetry Wrapper & CLI
├── deploy/         # Application Dockerfile & Swarm Stack (otel-test)
├── local/          # Observability Infrastructure Swarm Stack (otel-infra)
├── scripts/        # Automation & Testing scripts
└── certs/          # (Gitignored) Generated TLS Certificates
```

### Key Features
* **Memory Safe**: Utilizes `weakref` dictionaries internally to avoid instrument memory leaks over long-running processes.
* **Thread Safe**: Singleton Registry pattern ensures metric providers are initialized exactly once across all application threads.
* **Separated Stacks**: Follows Swarm best practices by separating the Application (`otel-test`) from the Infrastructure (`otel-infra`).
* **Encrypted Metrics**: The OpenTelemetry Collector uses custom TLS certificates to export data securely over HTTPS to the Prometheus scraper.
* **Internal Routing**: Utilizes Docker Swarm custom internal aliases, removing the need to expose ports to the `localhost` unnecessarily.

---

## 🚀 Getting Started

### 1. Generate TLS Certificates
Before deploying the metrics infrastructure, generate the self-signed TLS certificates required for secure OTel-to-Prometheus communication.

```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/otel.key -out certs/otel.crt \
  -subj "/CN=otel-collector" -addext "subjectAltName = DNS:otel-collector"
```

### 2. Deploy the Observability Infrastructure
Deploy the `otel-infra` stack, which consists of the OpenTelemetry Collector, Prometheus, and Grafana.

```bash
# Create the shared backend network
docker network create -d overlay --attachable otel-net

# Deploy the infrastructure stack
docker stack deploy -c ./local/docker-compose.yml otel-infra
```

### 3. Deploy your Application
The Python wrapper runs as its own unified application within the Swarm, communicating natively with the metric endpoint seamlessly over the internal network. 

```bash
# Build the application image
docker build -t otel-wrapper:latest -f deploy/Dockerfile .

# Deploy the application 
docker stack deploy -c ./deploy/docker-compose.yml otel-test
```

*(Note: The `otel-test` stack is configured to run `./scripts/automation_script.sh` on boot to emit 5 sample metrics).*

---

## 📈 Viewing Metrics

The infrastructure binds its User Interfaces to your machine using Docker Swarm's `host` port publishing mode, ensuring direct localhost accessibility. 

1. **Grafana**: Available at `http://localhost:3000`
2. **Prometheus**: Available at `http://localhost:9090/query`

**Adding Prometheus to Grafana**
When you add the Data Source in the Grafana UI, utilize the container's built-in Swarm network alias:
`http://prometheus:9090`

---

## 💻 Python Library Usage

The `otel_lib.py` library abstracts away the boilerplate of the OpenTelemetry API.

```python
from src.otel_lib import MetricsRegistry

# 1. Initialize the Registry automatically
registry = MetricsRegistry()

# 2. Emit a simple counter
registry.emit_counter("app.jobs.started", 1.0, {"type": "cron"})

# 3. Emit complex metrics (UpDownCounters, Histograms)
registry.emit_up_down_counter("app.queue.size", -5.0, {"queue": "priority"})
registry.emit_histogram("app.request.duration", 13.5, {"route": "/api/users"})
```

---

*This project was developed with a focus on Swarm interoperability, separation of concerns, and metric validation.*
