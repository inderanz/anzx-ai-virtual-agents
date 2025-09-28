# Cloud Monitoring & Observability Guide

## Overview

This guide covers the comprehensive observability setup for the Cricket Agent platform, including structured logging, metrics collection, distributed tracing, and alerting policies.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cricket Agent │    │  Cricket Bridge │    │   Website UI    │
│   (FastAPI)     │    │   (Node.js)     │    │   (Static)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │Cloud Logging│ │Cloud Monitor│ │Cloud Trace │ │Error Report │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Services & Observability

### 1. Cricket Agent (Python FastAPI)

**Logging:**
- Structured JSON logs with `structlog`
- Google Cloud Logging integration
- Request/response tracking with latency
- Intent classification and entity extraction logs
- PlayHQ API call logs with timing
- Vector store query logs
- Error reporting to Cloud Error Reporting

**Metrics:**
- Request count and error rate
- P95 latency tracking
- Token usage (input/output)
- Intent distribution
- PlayHQ API call metrics
- Vector store query metrics
- Cache hit/miss rates

**Tracing:**
- OpenTelemetry distributed tracing
- FastAPI request tracing
- HTTP client instrumentation
- PlayHQ API call traces
- Vector store operation traces

### 2. Cricket Bridge (Node.js)

**Logging:**
- Structured JSON logs with Winston
- WhatsApp connection/disconnection events
- Message forwarding logs (without content)
- Reply delivery tracking
- Rate limiting events
- Session management logs

**Metrics:**
- Message count and forward rate
- Agent response latency
- Error count by type
- WhatsApp connection status
- Session persistence metrics

**Tracing:**
- Express.js request tracing
- Axios HTTP client tracing
- WhatsApp message flow traces

## Alert Policies

### 1. High Latency Alerts

**Cricket Agent P95 Latency > 5s**
```yaml
displayName: "Cricket Agent High Latency"
conditions:
  - displayName: "P95 latency > 5s"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-agent"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 5000
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_DELTA
          crossSeriesReducer: REDUCE_PERCENTILE_95
          groupByFields:
            - resource.labels.service_name
```

**Cricket Bridge Forward Latency > 2s**
```yaml
displayName: "Cricket Bridge High Forward Latency"
conditions:
  - displayName: "Forward latency > 2s"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-bridge"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 2000
      duration: 300s
```

### 2. Error Rate Alerts

**Cricket Agent Error Rate > 5%**
```yaml
displayName: "Cricket Agent High Error Rate"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-agent"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_MEAN
```

**Cricket Bridge Error Rate > 10%**
```yaml
displayName: "Cricket Bridge High Error Rate"
conditions:
  - displayName: "Error rate > 10%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-bridge"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.10
      duration: 300s
```

### 3. Service Health Alerts

**Cricket Agent Health Check Failures**
```yaml
displayName: "Cricket Agent Health Check Failures"
conditions:
  - displayName: "Health check failures"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-agent" AND jsonPayload.event="health_check_failed"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0
      duration: 60s
```

**WhatsApp Connection Failures**
```yaml
displayName: "WhatsApp Connection Failures"
conditions:
  - displayName: "Connection failures"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="cricket-bridge" AND jsonPayload.event="whatsapp_disconnected"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0
      duration: 60s
```

### 4. Data Sync Alerts

**PlayHQ API Error Rate > 20%**
```yaml
displayName: "PlayHQ API High Error Rate"
conditions:
  - displayName: "PlayHQ API errors > 20%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND jsonPayload.event="playhq_api_call" AND jsonPayload.status_code>=400'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.20
      duration: 300s
```

**Data Sync Job Failures**
```yaml
displayName: "Data Sync Job Failures"
conditions:
  - displayName: "Sync job failures"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND jsonPayload.event="data_refresh" AND jsonPayload.status="failed"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0
      duration: 60s
```

### 5. Resource Utilization Alerts

**High Memory Usage > 80%**
```yaml
displayName: "High Memory Usage"
conditions:
  - displayName: "Memory usage > 80%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.80
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
```

**High CPU Usage > 90%**
```yaml
displayName: "High CPU Usage"
conditions:
  - displayName: "CPU usage > 90%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.90
      duration: 300s
```

## Dashboard Configuration

### 1. Cricket Agent Dashboard

**Key Metrics:**
- Request rate (requests/min)
- P95 latency (ms)
- Error rate (%)
- Token usage (tokens/min)
- Intent distribution
- PlayHQ API call rate
- Vector store query rate

**Logs:**
- Recent errors
- High latency requests
- Intent classification failures
- PlayHQ API errors

### 2. Cricket Bridge Dashboard

**Key Metrics:**
- Message rate (messages/min)
- Forward rate (forwards/min)
- Reply rate (replies/min)
- Agent latency (ms)
- WhatsApp connection status
- Error rate (%)

**Logs:**
- Connection events
- Message forwarding logs
- Rate limiting events
- Session management

### 3. System Overview Dashboard

**Key Metrics:**
- Service health status
- Overall request rate
- End-to-end latency
- Error rate by service
- Resource utilization

## Log Queries

### 1. High Latency Requests
```sql
resource.type="cloud_run_revision"
resource.labels.service_name="cricket-agent"
jsonPayload.latency_ms>5000
```

### 2. PlayHQ API Errors
```sql
resource.type="cloud_run_revision"
jsonPayload.event="playhq_api_call"
jsonPayload.status_code>=400
```

### 3. WhatsApp Connection Issues
```sql
resource.type="cloud_run_revision"
resource.labels.service_name="cricket-bridge"
jsonPayload.event="whatsapp_disconnected"
```

### 4. Intent Classification Failures
```sql
resource.type="cloud_run_revision"
resource.labels.service_name="cricket-agent"
jsonPayload.event="intent_classification_failed"
```

## Monitoring Setup

### 1. Enable APIs
```bash
# Enable required Google Cloud APIs
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable cloudtrace.googleapis.com
gcloud services enable clouderrorreporting.googleapis.com
```

### 2. Deploy Alert Policies
```bash
# Deploy alert policies
gcloud alpha monitoring policies create --policy-from-file=alerts/high-latency.yaml
gcloud alpha monitoring policies create --policy-from-file=alerts/error-rate.yaml
gcloud alpha monitoring policies create --policy-from-file=alerts/health-checks.yaml
```

### 3. Setup Dashboards
```bash
# Import dashboards
gcloud alpha monitoring dashboards create --config-from-file=dashboards/cricket-agent.yaml
gcloud alpha monitoring dashboards create --config-from-file=dashboards/cricket-bridge.yaml
gcloud alpha monitoring dashboards create --config-from-file=dashboards/system-overview.yaml
```

## Local Development

### 1. Cricket Agent
```bash
# Install dependencies
cd services/cricket-agent
pip install -r requirements.txt

# Run with observability
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Check metrics
curl http://localhost:8002/metrics
```

### 2. Cricket Bridge
```bash
# Install dependencies
cd services/cricket-bridge
npm install

# Run with observability
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
npm run dev

# Check metrics
curl http://localhost:8003/metrics
```

## Production Deployment

### 1. Cloud Run Configuration
```yaml
# cricket-agent service
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: cricket-agent
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/cricket-agent
        ports:
        - containerPort: 8002
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/credentials/service-account.json"
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

### 2. Service Account Permissions
```bash
# Create service account with required permissions
gcloud iam service-accounts create cricket-agent-sa

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/errorreporting.writer"
```

## Troubleshooting

### 1. Common Issues

**OpenTelemetry Setup Failures:**
- Check service account permissions
- Verify API enablement
- Check network connectivity

**High Memory Usage:**
- Review latency sample retention
- Check for memory leaks in metrics collection
- Adjust Cloud Run memory limits

**Missing Metrics:**
- Verify OpenTelemetry configuration
- Check metric export intervals
- Review Cloud Monitoring quotas

### 2. Debug Commands

```bash
# Check service health
curl http://localhost:8002/healthz
curl http://localhost:8003/healthz

# View metrics
curl http://localhost:8002/metrics
curl http://localhost:8003/metrics

# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

## Cost Optimization

### 1. Log Retention
- Set log retention to 30 days for non-critical logs
- Use log-based metrics for frequently queried data
- Implement log sampling for high-volume events

### 2. Metrics Optimization
- Use custom metrics sparingly
- Implement metric aggregation
- Set appropriate export intervals

### 3. Alert Optimization
- Use composite alerts for related conditions
- Implement alert suppression during maintenance
- Use notification channels efficiently

## Security Considerations

### 1. Log Privacy
- Never log sensitive data (API keys, tokens, PII)
- Use anonymization for user identifiers
- Implement log access controls

### 2. Metric Security
- Sanitize metric labels
- Avoid exposing internal system details
- Use secure metric export endpoints

### 3. Alert Security
- Secure notification channels
- Implement alert access controls
- Monitor alert policy changes

## Next Steps

1. **Implement Custom Dashboards** for specific use cases
2. **Add SLO Monitoring** for service level objectives
3. **Setup Incident Response** workflows
4. **Implement Log Analytics** for business insights
5. **Add Performance Testing** with observability
6. **Setup Cost Monitoring** for resource optimization
