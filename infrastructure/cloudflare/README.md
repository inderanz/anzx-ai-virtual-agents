# Cloudflare Worker for Cricket Agent Proxy

This directory contains the Cloudflare Worker implementation that proxies `/api/cricket/*` requests to the cricket-agent Cloud Run service.

## Files

- `worker.js` - Cloudflare Worker implementation
- `wrangler.toml.tmpl` - Worker configuration template
- `test-worker.sh` - Test script for validating Worker functionality

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │ Cloudflare CDN │    │ Cricket Agent  │
│   (anzx.ai)     │    │   + Worker     │    │  (Cloud Run)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ GET /api/cricket/*    │                       │
         ├──────────────────────►│                       │
         │                       │ Proxy to Cloud Run    │
         │                       ├──────────────────────►│
         │                       │                       │
         │ Response + CORS       │ Response              │
         │◄──────────────────────┤◄──────────────────────┤
```

## Worker Features

### Request Handling
- **Path Mapping:** `/api/cricket/healthz` → `/healthz`
- **Method Forwarding:** Preserves HTTP method (GET, POST, etc.)
- **Header Forwarding:** Forwards all request headers
- **Body Forwarding:** Preserves request body for POST requests

### CORS Support
- **Origin:** Allows requests from `https://anzx.ai`
- **Methods:** Supports GET, POST, PUT, DELETE, OPTIONS
- **Headers:** Allows Content-Type, Authorization, X-Requested-With
- **Preflight:** Handles OPTIONS requests with 204 response

### Error Handling
- **Proxy Errors:** Returns 502 with error details
- **CORS Headers:** Always includes CORS headers in responses
- **Logging:** Logs errors to Cloudflare console

## Configuration

The Worker is configured via `wrangler.toml.tmpl` with the following placeholders:

```toml
name = "${CLOUDFLARE_WORKER_NAME}"
account_id = "${CLOUDFLARE_ACCOUNT_ID}"
routes = [
  { pattern = "${CLOUDFLARE_ROUTE_PATTERN}", zone_id = "${CLOUDFLARE_ZONE_ID}" }
]
[vars]
CRICKET_AGENT_URL = "${CRICKET_AGENT_URL}"
```

### Required Secrets

The following secrets must be configured in Google Secret Manager:

- `CLOUDFLARE_API_TOKEN` - Cloudflare API token
- `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID
- `CLOUDFLARE_ZONE_ID` - Zone ID for anzx.ai
- `CLOUDFLARE_WORKER_NAME` - Worker name (e.g., `anzx-cricket-proxy`)
- `CLOUDFLARE_ROUTE_PATTERN` - Route pattern (e.g., `anzx.ai/api/cricket*`)

## Deployment

### Automatic Deployment (via Cloud Build)

The Worker is deployed automatically when `_CLOUDFLARE_DEPLOY=true` is set in the Cloud Build trigger:

```bash
gcloud builds triggers create github \
  --repo-name=anzx-ai-virtual-agents \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=infrastructure/cloudbuild/pipelines/cricket-deploy.yaml \
  --substitutions=_CLOUDFLARE_DEPLOY=true \
  --name=cricket-deploy-with-cloudflare
```

### Manual Deployment

```bash
# 1. Render wrangler.toml from secrets
CF_ACCOUNT_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ACCOUNT_ID)"
CF_ZONE_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ZONE_ID)"
CF_WORKER_NAME="$(gcloud secrets versions access latest --secret=CLOUDFLARE_WORKER_NAME)"
CF_ROUTE_PATTERN="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ROUTE_PATTERN)"
CRICKET_AGENT_URL="https://cricket-agent-xxxxx-uc.a.run.app"

sed -e "s|\${CLOUDFLARE_ACCOUNT_ID}|$CF_ACCOUNT_ID|g" \
    -e "s|\${CLOUDFLARE_ZONE_ID}|$CF_ZONE_ID|g" \
    -e "s|\${CLOUDFLARE_WORKER_NAME}|$CF_WORKER_NAME|g" \
    -e "s|\${CLOUDFLARE_ROUTE_PATTERN}|$CF_ROUTE_PATTERN|g" \
    -e "s|\${CRICKET_AGENT_URL}|$CRICKET_AGENT_URL|g" \
    wrangler.toml.tmpl > wrangler.toml

# 2. Deploy with wrangler
CF_API_TOKEN="$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)"
export CF_API_TOKEN

npm i -g wrangler@latest
wrangler deploy --config wrangler.toml --name "$CF_WORKER_NAME"

unset CF_API_TOKEN
```

## Testing

### Automated Testing

Use the provided test script:

```bash
# Test against anzx.ai
./test-worker.sh anzx.ai

# Test against custom domain
./test-worker.sh your-domain.com
```

### Manual Testing

```bash
# Health check
curl -I https://anzx.ai/api/cricket/healthz

# Cricket query
curl -X POST https://anzx.ai/api/cricket/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"text":"Show me the fixtures for Caroline Springs", "source":"web"}'

# CORS preflight
curl -X OPTIONS https://anzx.ai/api/cricket/v1/ask \
  -H 'Origin: https://anzx.ai' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: Content-Type'
```

### Expected Responses

**Health Check:**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://anzx.ai
Content-Type: application/json

{"ok":true,"env":"dev","rag":"vertex_rag","mode":"public"}
```

**Cricket Query:**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://anzx.ai
Content-Type: application/json

{"answer":"I don't have information about team **gs**.","meta":{"intent":"fixtures_list"}}
```

**CORS Preflight:**
```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://anzx.ai
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With
```

## Monitoring

### Cloudflare Dashboard
- View Worker logs in Cloudflare dashboard
- Monitor request volume and response times
- Check error rates and status codes

### Google Cloud Logging
- Worker deployment logs in Cloud Build
- Secret access logs in Secret Manager
- Deployment state in GCS bucket

## Troubleshooting

### Common Issues

**Worker Not Deploying:**
- Check all required secrets exist
- Verify `_CLOUDFLARE_DEPLOY=true` is set
- Check Cloudflare API token permissions
- Review Cloud Build logs

**Proxy Errors:**
- Verify cricket-agent Cloud Run is healthy
- Check Worker logs in Cloudflare dashboard
- Test direct cricket-agent URL
- Verify CORS configuration

**CORS Issues:**
- Check Origin header is `https://anzx.ai`
- Verify CORS headers in response
- Test with browser developer tools
- Check preflight request handling

### Debug Commands

```bash
# Check Worker status
wrangler tail --name anzx-cricket-proxy

# View Worker configuration
wrangler whoami

# Test Worker locally
wrangler dev --local
```

## Security Considerations

### Secret Management
- Secrets are read from Google Secret Manager
- No secrets are logged or echoed
- API token is only used for deployment
- Environment variables are cleaned after use

### CORS Configuration
- Only allows requests from `https://anzx.ai`
- Supports necessary HTTP methods
- Includes appropriate headers
- Handles preflight requests

### Request Forwarding
- Preserves original request method and headers
- Forwards request body for POST requests
- Maintains query parameters
- Returns original response with CORS headers

## Performance

### Cloudflare Benefits
- Global CDN distribution
- Edge computing capabilities
- Automatic HTTPS
- DDoS protection

### Optimization
- Worker runs at edge locations
- Minimal latency for global users
- Automatic scaling
- No cold start issues

## Cost Considerations

### Cloudflare Worker
- Free tier: 100,000 requests/day
- Paid tier: $5/month for 10M requests
- No additional bandwidth costs

### Google Cloud
- No additional costs for Worker deployment
- Uses existing Cloud Run services
- Secret Manager access is included
- GCS storage for deployment state
