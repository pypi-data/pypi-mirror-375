# SQS Worker Metrics with Prometheus and Grafana

This example demonstrates how to monitor SQS worker metrics using Prometheus and Grafana.

## Architecture

- **Worker**: SQS worker that processes messages and exposes metrics on port 9090
- **LocalStack**: Local AWS SQS service for testing
- **Prometheus**: Metrics collection and storage (accessible on port 9091)
- **Grafana**: Metrics visualization dashboard (accessible on port 3000)

## Metrics Exposed

The SQS worker exposes the following metrics:

1. **`sqs_manager_exceptions_total`** (Counter): Total number of exceptions encountered
2. **`sqs_manager_work_latency_seconds`** (Histogram): Latency of message processing

## Usage

### 1. Start the Stack

```bash
docker-compose up -d
```

This will start:
- LocalStack (SQS service)
- SQS Worker with metrics enabled
- Prometheus
- Grafana

### 2. Send Test Messages

Install boto3 if you haven't already:
```bash
pip install boto3
```

Then run the test script to send messages:
```bash
python send_test_messages.py
```

### 3. View Metrics

#### Prometheus (Raw Metrics)
- URL: http://localhost:9091
- You can query metrics directly using PromQL

Example queries:
- `sqs_manager_exceptions_total` - Total exceptions
- `rate(sqs_manager_work_latency_seconds_count[5m])` - Message processing rate
- `histogram_quantile(0.95, rate(sqs_manager_work_latency_seconds_bucket[5m]))` - 95th percentile latency

#### Grafana (Dashboard)
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`

The dashboard includes:
- Exception rate over time
- Total exceptions gauge
- Work latency percentiles (50th, 95th, 99th)
- Message processing rate

### 4. Clean Up

```bash
docker-compose down -v
```

## Configuration Files

- `prometheus.yml`: Prometheus configuration to scrape worker metrics
- `grafana/provisioning/`: Grafana auto-provisioning configuration
  - `datasources/prometheus.yml`: Prometheus datasource configuration
  - `dashboards/dashboards.yml`: Dashboard provider configuration
  - `dashboards/sqs-worker-dashboard.json`: Pre-built SQS worker dashboard

## Customization

You can modify the Grafana dashboard by:
1. Editing the JSON file directly, or
2. Making changes in the Grafana UI and exporting the updated dashboard

To add more metrics, modify the worker code to expose additional Prometheus metrics using the `metrics_instrumentator` object.
