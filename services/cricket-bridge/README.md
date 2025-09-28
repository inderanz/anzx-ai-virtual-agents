# Cricket Bridge Service

Production-ready Node service using Baileys MD that relays WhatsApp group messages to the cricket-agent `/v1/ask` endpoint.

## Features

- **WhatsApp Integration**: Uses Baileys MD for WhatsApp Web API
- **Session Persistence**: Supports GCS and Secret Manager for session storage
- **Message Filtering**: Group filtering, prefix/mention detection, deduplication
- **Rate Limiting**: Per-group rate limiting to prevent spam
- **Security**: Bearer token authentication for relay endpoint
- **Observability**: Structured JSON logging with privacy protection
- **Health Checks**: Built-in health monitoring

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. **Start the service**:
   ```bash
   npm run dev
   ```

4. **Scan QR code** (first time only):
   - The QR code will appear in the terminal
   - Scan it with your WhatsApp mobile app
   - The session will be saved for future runs

### Production Deployment

1. **Build the service**:
   ```bash
   npm run build
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy cricket-bridge \
     --source . \
     --platform managed \
     --region australia-southeast1 \
     --min-instances 1 \
     --max-instances 10 \
     --concurrency 5 \
     --cpu-always-allocated \
     --set-env-vars CRICKET_AGENT_URL=https://cricket-agent-xxx.run.app
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8003` |
| `CRICKET_AGENT_URL` | Cricket agent endpoint | `http://localhost:8002` |
| `TRIGGER_PREFIX` | Message trigger prefix | `!cscc` |
| `RELAY_TOKEN` | Bearer token for relay endpoint | `local-dev` |
| `GCS_BUCKET` | GCS bucket for session storage | - |
| `SESSION_SECRET_NAME` | Secret Manager key for session | - |
| `ALLOWED_GROUPS` | Comma-separated group JIDs | - |
| `LOG_LEVEL` | Logging level | `info` |

### Session Storage

Choose one of the following options:

#### Option 1: Google Cloud Storage (Recommended)
```bash
GCS_BUCKET=your-cricket-bridge-bucket
```

#### Option 2: Secret Manager
```bash
SESSION_SECRET_NAME=projects/your-project/secrets/WHATSAPP_SESSION/versions/latest
```

#### Option 3: Local Development
If neither is configured, sessions are saved to `./session/` directory.

### Group Filtering

To restrict the bot to specific WhatsApp groups:

```bash
ALLOWED_GROUPS=120363123456789012@g.us,120363987654321098@g.us
```

## Usage

### Message Triggers

The bot responds to messages in the following ways:

1. **Prefix trigger**: Messages starting with `!cscc`
   ```
   !cscc list fixtures for Caroline Springs Blue U10
   ```

2. **Mention trigger**: Messages mentioning the bot
   ```
   @bot what are the upcoming matches?
   ```

### Example Interactions

**Fixtures List**:
```
User: !cscc list fixtures for Caroline Springs Blue U10
Bot: Here are the fixtures for **Caroline Springs Blue U10**:
     **Upcoming Fixtures:**
     - **Sat 12 Oct 2025, 9:00 AM** – vs Caroline Springs White U10 at Caroline Springs Oval (SCHEDULED)
     - **Sat 19 Oct 2025, 9:00 AM** – vs Melton U10 at Melton Oval (SCHEDULED)
```

**Ladder Position**:
```
User: !cscc where are Caroline Springs Blue U10 on the ladder?
Bot: **Caroline Springs Blue U10** is currently in **1st position** on the ladder.
     Stats: Played 5, Won 4, Lost 1, Points 10.
     *(As of Mon 06 Jan 2025, 2:30 PM)*
```

**Player Lookup**:
```
User: !cscc which team is John Smith in?
Bot: John Smith is part of **Caroline Springs Blue U10**.
```

## API Endpoints

### Health Check
```bash
GET /healthz
```

Response:
```json
{
  "ok": true,
  "connected": true,
  "me": "bot@s.whatsapp.net",
  "timestamp": "2025-01-06T02:30:00.000Z"
}
```

### Relay Endpoint
```bash
POST /relay
Headers: X-Relay-Token: your-token
Body: {
  "text": "list fixtures for Caroline Springs Blue U10",
  "team_hint": "team-id"
}
```

## Testing

Run the test suite:

```bash
npm test
```

Run tests with coverage:

```bash
npm run test:coverage
```

## Monitoring

### Logs

The service produces structured JSON logs:

```json
{
  "event": "message_received",
  "chatId": "abc123@g.us",
  "sender": "def456@s.whatsapp.net",
  "messageLength": 25,
  "isGroup": true,
  "timestamp": "2025-01-06T02:30:00.000Z"
}
```

### Health Monitoring

Monitor the `/healthz` endpoint for:
- WhatsApp connection status
- Service availability
- Bot identity

### Rate Limiting

The service implements per-group rate limiting:
- **Burst**: 3 messages per 2-second window
- **Window**: 2 seconds
- **Action**: Messages beyond limit are ignored

## Security

### Privacy Protection

- **No message content logging**: Only metadata is logged
- **Anonymized JIDs**: User and group identifiers are hashed
- **Secret masking**: Tokens and credentials are never logged

### Authentication

- **Relay endpoint**: Requires `X-Relay-Token` header
- **Group filtering**: Optional restriction to specific groups
- **Rate limiting**: Prevents spam and abuse

## Troubleshooting

### Common Issues

1. **QR Code not appearing**:
   - Ensure `NODE_ENV` is not set to `production`
   - Check that no existing session is interfering

2. **Messages not triggering**:
   - Verify the trigger prefix matches your configuration
   - Check if the group is in the allowed groups list
   - Ensure the message format is correct

3. **Session not persisting**:
   - Verify GCS bucket or Secret Manager permissions
   - Check that the service account has necessary roles

4. **Rate limiting issues**:
   - Adjust the rate limit configuration if needed
   - Check logs for rate limiting events

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=debug npm run dev
```

## Development

### Project Structure

```
src/
├── index.ts              # Main application entry point
├── forwarder.ts          # HTTP client for cricket-agent
├── logger.ts             # Structured logging
├── types.ts              # TypeScript type definitions
└── utils/
    ├── session.ts        # Session persistence (GCS/Secret Manager)
    └── filters.ts        # Message filtering and rate limiting

__tests__/
├── filters.test.ts       # Message filter tests
├── forwarder.test.ts     # HTTP client tests
├── session.test.ts       # Session management tests
└── setup.ts             # Jest test setup
```

### Adding Features

1. **New message triggers**: Update `MessageFilters` class
2. **Additional storage**: Extend `SessionManager` class
3. **New endpoints**: Add routes to Express app
4. **Enhanced logging**: Extend `CricketLogger` class

## Deployment

### Cloud Run Configuration

Recommended Cloud Run settings:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: cricket-bridge
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 5
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT/cricket-bridge
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
        env:
        - name: CRICKET_AGENT_URL
          value: "https://cricket-agent-xxx.run.app"
        - name: GCS_BUCKET
          value: "your-cricket-bridge-bucket"
```

### Workload Identity

For production, use Workload Identity instead of service account keys:

```bash
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT.svc.id.goog[default/cricket-bridge]" \
  cricket-bridge@PROJECT.iam.gserviceaccount.com
```

## License

MIT License - see LICENSE file for details.
