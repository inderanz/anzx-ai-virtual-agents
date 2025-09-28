# Caroline Springs CC Cricket Agent

Real-time cricket agent for Caroline Springs Cricket Club, powered by PlayHQ APIs and Google Vertex AI.

## Features

- **Real-time Cricket Data**: Fixtures, ladders, player stats, team rosters
- **Multi-channel Support**: Web chat and WhatsApp integration
- **Grounded Responses**: No hallucinations, data-driven answers
- **Fast Performance**: p50 < 3s response time
- **Scalable Architecture**: Cloud Run deployment with auto-scaling

## Architecture

```
[Web UI] ──┐
           ├── [Cricket Agent] ── [PlayHQ API] ── [Vector Store]
[WhatsApp] ─┘
```

## Quick Start

### Development Setup

1. **Install Dependencies**
   ```bash
   cd services/cricket-agent
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Service**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
   ```

4. **Test the API**
   ```bash
   curl http://localhost:8002/healthz
   curl -X POST http://localhost:8002/v1/ask \
     -H "Content-Type: application/json" \
     -d '{"text": "What are the fixtures for Caroline Springs Blue U10?"}'
   ```

### Docker Setup

1. **Build Image**
   ```bash
   docker build -t cricket-agent .
   ```

2. **Run Container**
   ```bash
   docker run -p 8002:8002 cricket-agent
   ```

## API Endpoints

### Health Checks
- `GET /healthz` - Basic health check
- `GET /healthz/detailed` - Detailed health with dependencies

### Cricket Agent
- `POST /v1/ask` - Ask cricket questions
- `POST /internal/refresh` - Refresh data (internal)

## Configuration

### Required Secrets

The cricket-agent requires the following secrets to be configured in Google Secret Manager:

1. **`PLAYHQ_API_KEY`** - PlayHQ API key for accessing cricket data
2. **`CSCC_IDS`** - JSON bundle containing Caroline Springs CC organization details
3. **`CRICKET_INTERNAL_TOKEN`** - Bearer token for `/internal/refresh` endpoint
4. **`PLAYHQ_PRIVATE_TOKEN`** - Private API token (only required if `PLAYHQ_MODE=private`)

### IDs Bundle Schema

The `CSCC_IDS` secret must contain a JSON object with the following structure:

```json
{
  "tenant": "ca",
  "org_id": "<guid>",
  "season_id": "<guid>",
  "grade_id": "<guid>",
  "teams": [
    {"name": "Caroline Springs Blue U10", "team_id": "<guid>"},
    {"name": "Caroline Springs White U10", "team_id": "<guid>"}
  ]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment | `dev` |
| `PORT` | Service port | `8080` |
| `GCP_PROJECT` | Google Cloud project ID | Required |
| `REGION` | GCP region | `australia-southeast1` |
| `VERTEX_LOCATION` | Vertex AI location | `australia-southeast1` |
| `VERTEX_MODEL` | Vertex AI model | `gemini-1.5-flash` |
| `EMBED_MODEL` | Embedding model | `text-embedding-005` |
| `PLAYHQ_MODE` | PlayHQ mode (public/private) | `public` |
| `VECTOR_BACKEND` | Vector store backend | `vertex_rag` |
| `SECRET_PLAYHQ_API_KEY` | PlayHQ API key secret ref | Required |
| `SECRET_IDS_BUNDLE` | CSCC IDs bundle secret ref | Required |
| `SECRET_INTERNAL_TOKEN` | Internal token secret ref | Required |
| `SECRET_PLAYHQ_PRIVATE_TOKEN` | Private token secret ref | Required for private mode |

### Workload Identity Setup

For production deployment on Cloud Run:

1. **Enable Workload Identity** on your Cloud Run service
2. **Grant Secret Manager access** to the service account
3. **Use Secret Manager references** in your environment variables

### Security Notes

- **Private Mode**: When `PLAYHQ_MODE=private`, contact information in rosters is preserved
- **Public Mode**: When `PLAYHQ_MODE=public`, PII is stripped from responses
- **Secret Logging**: Secret values are never logged; only references are shown in logs
- **Local Development**: Raw values are allowed for local dev but not recommended for production

## 🚀 Local Development Guide

### Quick Start

#### 1. **Environment Setup**
```bash
# Navigate to cricket-agent directory
cd services/cricket-agent

# Copy environment template
cp env.example .env

# Edit .env with your local values
nano .env  # or use your preferred editor
```

#### 2. **Configure Environment Variables**
Edit `.env` file with your local development values:

```bash
# Application Environment
APP_ENV=dev
PORT=8080

# Google Cloud Configuration (optional for local dev)
GCP_PROJECT=your-project-id
REGION=australia-southeast1
VERTEX_LOCATION=australia-southeast1

# AI Models
VERTEX_MODEL=gemini-1.5-flash
EMBED_MODEL=text-embedding-005

# PlayHQ Configuration
PLAYHQ_MODE=public
VECTOR_BACKEND=vertex_rag

# Local Development Secrets (raw values for local dev)
SECRET_PLAYHQ_API_KEY=your-actual-playhq-api-key
SECRET_IDS_BUNDLE={"tenant":"ca","org_id":"your-org-id","season_id":"your-season-id","grade_id":"your-grade-id","teams":[{"name":"Caroline Springs Blue U10","team_id":"team-001"},{"name":"Caroline Springs White U10","team_id":"team-002"}]}
SECRET_INTERNAL_TOKEN=your-internal-token-for-refresh-endpoint

# Optional: Private mode token (only if PLAYHQ_MODE=private)
SECRET_PLAYHQ_PRIVATE_TOKEN=your-private-token
```

#### 3. **Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. **Run Tests**
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test suites
python3 -m pytest tests/test_config.py -v
python3 -m pytest tests/test_normalize.py -v
python3 -m pytest tests/test_playhq_client.py -v

# Run with coverage
python3 -m pytest --cov=app --cov=agent --cov-report=html
```

#### 5. **Start the Service**
```bash
# Development mode with auto-reload
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Production mode
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

#### 6. **Test the API**
```bash
# Health check
curl http://localhost:8080/healthz

# Expected response:
# {
#   "ok": true,
#   "env": "dev",
#   "rag": "vertex_rag",
#   "mode": "public",
#   "timestamp": "2025-01-20T10:30:00.000Z",
#   "service": "cricket-agent",
#   "version": "1.0.0"
# }

# Ask cricket question
curl -X POST http://localhost:8080/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "What are the fixtures for Caroline Springs Blue U10?", "source": "web"}'

# Internal refresh (requires token)
curl -X POST http://localhost:8080/internal/refresh \
  -H "X-Internal-Token: your-internal-token-for-refresh-endpoint"
```

### Development Workflow

#### **Daily Development**
```bash
# 1. Start development server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 2. In another terminal, run tests
python3 -m pytest tests/ -v

# 3. Test specific functionality
python3 -c "
from app.config import get_settings
settings = get_settings()
print(f'Mode: {settings.playhq_mode}')
print(f'Backend: {settings.vector_backend}')
"
```

#### **Testing Configuration**
```bash
# Test configuration loading
python3 -c "
import sys
sys.path.append('.')
from app.config import get_settings
try:
    settings = get_settings()
    print('✅ Configuration loaded successfully')
    print(f'App env: {settings.app_env}')
    print(f'Port: {settings.port}')
    print(f'PlayHQ mode: {settings.playhq_mode}')
    print(f'Vector backend: {settings.vector_backend}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

#### **Docker Development**
```bash
# Build Docker image
docker build -t cricket-agent .

# Run with environment file
docker run -p 8080:8080 --env-file .env cricket-agent

# Run with environment variables
docker run -p 8080:8080 \
  -e APP_ENV=dev \
  -e PORT=8080 \
  -e SECRET_PLAYHQ_API_KEY=your-api-key \
  -e SECRET_IDS_BUNDLE='{"tenant":"ca",...}' \
  -e SECRET_INTERNAL_TOKEN=your-token \
  cricket-agent
```

### Troubleshooting

#### **Common Issues**

1. **Configuration Validation Errors**
   ```
   Error: SECRET_PLAYHQ_API_KEY is required for public mode
   ```
   **Solution**: Ensure all required secrets are set in `.env` file

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'pydantic_settings'
   ```
   **Solution**: Install missing dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. **Secret Manager Errors (Local Dev)**
   ```
   Error: Failed to load secret projects/...
   ```
   **Solution**: Use raw values in `.env` for local development, not Secret Manager references

4. **Port Already in Use**
   ```
   Error: [Errno 48] Address already in use
   ```
   **Solution**: Change port or kill existing process
   ```bash
   # Change port
   python3 -m uvicorn app.main:app --port 8081
   
   # Or kill existing process
   lsof -ti:8080 | xargs kill -9
   ```

#### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Or set in .env
echo "LOG_LEVEL=DEBUG" >> .env
```

#### **Testing Specific Features**
```bash
# Test PlayHQ client
python3 -c "
from agent.tools.playhq import PlayHQClient
# Test client initialization
"

# Test normalization
python3 -c "
from agent.tools.normalize import CricketDataNormalizer
normalizer = CricketDataNormalizer()
print('Normalizer initialized successfully')
"

# Test models
python3 -c "
from models.team import Team, Player
team = Team(id='test', name='Test Team')
print(f'Team created: {team.name}')
"
```

### Development Tips

#### **Environment Management**
```bash
# Use different .env files for different environments
cp .env .env.local
cp .env .env.test
cp .env .env.prod

# Load specific environment
export ENV_FILE=.env.local
python3 -m uvicorn app.main:app --reload
```

#### **Testing Workflow**
```bash
# Run tests before committing
python3 -m pytest tests/ -v --cov=app --cov=agent

# Run specific test categories
python3 -m pytest -m unit -v
python3 -m pytest -m integration -v
python3 -m pytest -m config -v
```

#### **Code Quality**
```bash
# Format code (if using black)
black app/ tests/

# Lint code (if using flake8)
flake8 app/ tests/

# Type checking (if using mypy)
mypy app/
```

### Production vs Development

| Aspect | Development | Production |
|--------|-------------|------------|
| **Secrets** | Raw values in `.env` | Secret Manager references |
| **Logging** | Console output | Structured JSON logs |
| **Port** | 8080 (configurable) | 8080 (Cloud Run) |
| **Workers** | 1 (reload enabled) | 4 (production) |
| **Validation** | Strict (fails fast) | Strict (fails fast) |
| **Mode** | `dev` | `prod` |

### Data Sync Testing

Test the internal refresh endpoint:

```bash
# Full refresh
curl -X POST http://localhost:8080/internal/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-internal-token" \
  -d '{"scope": "all"}'

# Team-specific refresh
curl -X POST http://localhost:8080/internal/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-internal-token" \
  -d '{"scope": "team", "id": "team-123"}'

# Match-specific refresh
curl -X POST http://localhost:8080/internal/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-internal-token" \
  -d '{"scope": "match", "id": "match-456"}'

# Ladder refresh
curl -X POST http://localhost:8080/internal/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-internal-token" \
  -d '{"scope": "ladder", "id": "grade-789"}'
```

### Manual Sync Execution

Run sync jobs directly from the command line:

```bash
# Full refresh
python -m jobs.sync

# Team-specific refresh
python -m jobs.sync team team-123

# Match-specific refresh
python -m jobs.sync match match-456

# Ladder refresh
python -m jobs.sync ladder grade-789
```

### Next Steps

After local development is working:

1. **Test with real PlayHQ data** (if API keys are available)
2. **Test sync functionality** with manual commands
3. **Deploy to Cloud Run** with Workload Identity
4. **Set up Cloud Scheduler** for automated sync
5. **Set up CI/CD pipeline** integration

## Testing

### Run Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov=agent --cov-report=html
```

### Test Categories
- `pytest -m unit` - Unit tests only
- `pytest -m integration` - Integration tests
- `pytest -m playhq` - PlayHQ API tests

## Deployment

### Cloud Run Deployment

1. **Build and Push**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/cricket-agent
   ```

2. **Deploy**
   ```bash
   gcloud run deploy cricket-agent \
     --image gcr.io/PROJECT_ID/cricket-agent \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### CI/CD Integration

The service integrates with the existing Cloud Build pipeline:

```yaml
# cloudbuild-cricket-agent.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/cricket-agent', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/cricket-agent']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'cricket-agent', '--image', 'gcr.io/$PROJECT_ID/cricket-agent']
```

## Monitoring

### Logging
- Structured JSON logs
- Request/response tracking
- Error monitoring
- Performance metrics

### Metrics
- Response latency (p50, p95)
- PlayHQ API call success rate
- Vector store query performance
- Error rates by endpoint

### Alerts
- p95 latency > 5s
- Error rate > 2%
- PlayHQ API failures
- Sync job failures

## Development

### Code Structure

```
services/cricket-agent/
├── app/                    # FastAPI application
│   ├── main.py            # Main app and endpoints
│   ├── config.py          # Configuration management
│   └── observability.py   # Logging and metrics
├── agent/                 # Agent logic
│   └── tools/             # Tools and utilities
│       └── playhq.py     # PlayHQ API client
├── models/                # Data models
│   ├── team.py           # Team model
│   ├── fixture.py        # Fixture model
│   ├── scorecard.py      # Scorecard model
│   ├── ladder.py         # Ladder model
│   └── roster.py         # Roster model
├── jobs/                 # Background jobs
│   └── sync.py          # Data sync job
├── tests/                # Test suite
└── requirements.txt      # Dependencies
```

### Adding New Features

1. **New Data Sources**: Add to `agent/tools/`
2. **New Models**: Add to `models/`
3. **New Endpoints**: Add to `app/main.py`
4. **New Tests**: Add to `tests/`

## Troubleshooting

### Common Issues

1. **PlayHQ API Errors**
   - Check API key and tenant ID
   - Verify network connectivity
   - Check rate limits

2. **Vector Store Issues**
   - Verify Vertex AI configuration
   - Check embeddings model access
   - Monitor quota usage

3. **Performance Issues**
   - Check response times in logs
   - Monitor PlayHQ API latency
   - Review vector store query performance

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m uvicorn app.main:app --reload
```

## Private Mode & Webhooks

The cricket agent supports two modes of operation:

### Public Mode (Default)
- Uses public PlayHQ API endpoints
- Data is fetched on-demand via sync jobs
- No real-time updates
- Suitable for most use cases

### Private Mode
- Enables real-time webhook updates from PlayHQ
- Requires private PlayHQ API access
- Webhook endpoint: `POST /webhooks/playhq`
- Requires additional secrets configuration

#### Enabling Private Mode

1. **Set Environment Variable:**
   ```bash
   export PLAYHQ_MODE=private
   ```

2. **Configure Additional Secrets:**
   ```bash
   # PlayHQ private token
   export SECRET_PLAYHQ_PRIVATE_TOKEN=projects/PROJECT_ID/secrets/PLAYHQ_PRIVATE_TOKEN/versions/latest
   
   # PlayHQ webhook secret
   export SECRET_PLAYHQ_WEBHOOK_SECRET=projects/PROJECT_ID/secrets/PLAYHQ_WEBHOOK_SECRET/versions/latest
   ```

3. **Webhook Configuration:**
   - Configure PlayHQ to send webhooks to: `https://your-domain.com/webhooks/playhq`
   - Use the webhook secret for signature verification
   - Supported events: `fixture_update`, `scorecard_update`, `ladder_update`, `roster_update`

#### Webhook Security

The webhook endpoint is protected by:
- **Mode Check:** Only available when `PLAYHQ_MODE=private`
- **Signature Verification:** Uses HMAC-SHA256 with webhook secret
- **Header Required:** `X-PlayHQ-Signature` header must be present

#### Webhook Payload Format

```json
{
  "event_type": "fixture_update",
  "timestamp": "2025-09-28T10:00:00Z",
  "data": {
    "fixture_id": "fixture_123",
    "team_id": "team_123",
    "season_id": "season_123",
    "grade_id": "grade_123",
    "status": "scheduled",
    "venue": "Test Ground",
    "start_time": "2025-09-28T10:00:00Z",
    "opponent": "Opponent Team"
  }
}
```

#### Testing Webhooks Locally

```bash
# Test webhook signature
python -c "
import hmac, hashlib, json
payload = json.dumps({'test': 'data'}).encode()
secret = 'your_webhook_secret'
signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
print(f'X-PlayHQ-Signature: {signature}')
"

# Send test webhook
curl -X POST http://localhost:8002/webhooks/playhq \
  -H "Content-Type: application/json" \
  -H "X-PlayHQ-Signature: YOUR_SIGNATURE" \
  -d '{"event_type": "fixture_update", "timestamp": "2025-09-28T10:00:00Z", "data": {...}}'
```

## Support

For issues and questions:
- Check logs: `gcloud logging read "resource.type=cloud_run_revision"`
- Monitor metrics: Cloud Console > Cloud Run > cricket-agent
- Review documentation: `/docs` endpoint

## License

MIT License - see LICENSE file for details.
