# PC Health Monitoring

A containerized observability project that collects system and application
metrics, exposes them in Prometheus format, and visualizes them in Grafana. It
demonstrates practical DevOps workflows around Docker, monitoring, alerting,
automated provisioning, testing, and CI security checks.

## Stack

- Python 3.11
- `psutil` for system metrics
- Prometheus Client for the `/metrics` endpoint
- Prometheus for scraping and storing metrics
- Grafana for visualization
- Node Exporter for host-level Linux metrics
- GitHub Actions for CI
- Docker Compose for local orchestration
- pytest, Ruff, mypy, Bandit, pip-audit, and Trivy for quality and security

## Architecture

```text
Python exporter :8080  --+-->  Prometheus :9090  -->  Grafana :3000
                         |
Node Exporter :9100  ----+
```

## Run locally

Requirements: Docker Desktop with Docker Compose.

```powershell
Copy-Item .env.example .env
# Edit .env and replace GRAFANA_ADMIN_PASSWORD with a long random password.
docker compose up --build
```

The `.env` file is intentionally ignored by Git. Commit only `.env.example`
and never commit real passwords or tokens.

After startup:

- Metrics: http://localhost:8080/metrics
- Health check: http://localhost:8080/health
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Node Exporter: http://localhost:9100/metrics

Log in to Grafana with the `admin` user and the password configured in `.env`.
The Prometheus datasource and the `PC Health` dashboard are provisioned
automatically.

Stop the stack with:

```powershell
docker compose down
```

## Metrics

The exporter currently exposes:

- `pc_cpu_usage_percent`
- `pc_memory_usage_percent`
- `pc_cpu_frequency_mhz`
- `pc_disk_usage_percent`
- `pc_process_cpu_percent`
- `pc_process_memory_bytes`
- `pc_process_threads`
- `pc_app_info{version="..."}`

The exporter provides `/health` for container healthchecks and `/metrics` for
Prometheus scraping.

The disk path and collection interval can be configured with `DISK_PATH` and
`METRICS_INTERVAL` in `.env`.

Prometheus is configured in [monitoring/prometheus.yml](monitoring/prometheus.yml),
with alert rules in [monitoring/alerts.yml](monitoring/alerts.yml).

Grafana automatically provisions the Prometheus datasource and the PC Health
dashboard from `monitoring/grafana/provisioning` and
`monitoring/grafana/dashboards`.

## Alerting

Prometheus evaluates the rules in `monitoring/alerts.yml` for high CPU usage,
high memory usage, low disk space, and unavailable exporters. The rules are
loaded automatically by the Compose stack.

Alert notifications are not configured by default. To send notifications,
configure contact points and notification policies in Grafana or add an
Alertmanager service.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_PORT` | `8080` | Host port for the exporter |
| `DISK_PATH` | `/` | Disk path measured by `psutil` |
| `METRICS_INTERVAL` | `5` | Collection interval in seconds |
| `APP_VERSION` | `0.1.0` | Version exposed as `pc_app_info` |
| `PROMETHEUS_PORT` | `9090` | Host port for Prometheus |
| `GRAFANA_PORT` | `3000` | Host port for Grafana |
| `NODE_EXPORTER_PORT` | `9100` | Host port for Node Exporter |

## CI pipeline

Every push and pull request runs the following checks in GitHub Actions:

1. `pytest` runs the automated tests.
2. `ruff` checks Python code quality.
3. `mypy` checks type correctness.
4. `bandit` and `pip-audit` scan the code and dependencies for security issues.
5. Docker Compose configuration is validated.
6. The Docker image is built and scanned with Trivy for high and critical vulnerabilities.

The workflow is defined in `.github/workflows/ci.yml` and runs on every push
and pull request. It is intentionally a CI pipeline; deployment to a registry
or server requires adding repository-specific credentials and a release job.

## Development

Create a virtual environment and install development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the application directly:

```powershell
python app\main.py
```

Quality checks:

```powershell
pytest
ruff check .
mypy app
bandit -r app
pip-audit
```

## Project structure

```text
app/                 Python application and tests
monitoring/          Prometheus and Grafana configuration
  grafana/           Provisioning files and dashboards
.github/workflows/   CI configuration
Dockerfile           Application image definition
docker-compose.yml   Local monitoring stack
```

## Known limitation

When the exporter runs in Docker, `psutil` reports resources visible inside the
container. Node Exporter is included for host-level Linux monitoring, but Docker
Desktop on Windows runs Linux containers inside a virtual machine, so its
filesystem mounts may describe the Docker environment rather than Windows.

## License

This project is available under the MIT License.