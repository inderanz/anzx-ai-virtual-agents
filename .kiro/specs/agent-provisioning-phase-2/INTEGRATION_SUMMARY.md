# Phase 2 Integration Summary

## Existing Infrastructure Review

### ✅ Backend Services (Already Deployed on Cloud Run)

**Project:** `extreme-gecko-466211-t1`  
**Region:** `australia-southeast1`

#### core-api (FastAPI)
**Status:** ✅ Deployed and operational

**Existing Routers:**
- `/api/v1/auth` - Firebase authentication, JWT tokens
- `/api/v1/agents` - Agent creation, management, conversations
- `/api/v1/organizations` - Organization management
- `/api/v1/billing` - Stripe integration, subscriptions
- `/api/knowledge` - Document processing, RAG
- `/api/conversations` - Conversation management
- `/api/mcp` - MCP server integration
- `/api/email` - Email integration
- `/ws` - WebSocket support
- `/api/v1/compliance` - Compliance and audit logging

**Existing Services:**
- `vertex_ai_service.py` - Vertex AI Agent Builder integration
- `agent_service.py` - Agent lifecycle management
- `gcp_auth_service.py` - Workload Identity authentication
- `stripe_service.py` - Billing and subscriptions
- `hybrid_agent_orchestrator.py` - Multi-agent routing
- `conversation_service.py` - Conversation management
- `usage_tracking.py` - Usage metering

**Database:**
- PostgreSQL with pgvector (Cloud SQL)
- Models: User, Organization, Assistant, Conversation, Message
- Alembic migrations configured

#### agent-orchestration
**Status:** ✅ Ready for deployment
- Hybrid agent routing between Vertex AI and custom workflows

#### knowledge-service
**Status:** ✅ Ready for deployment
- Document processing (PDF, DOCX, CSV, URL)
- Vector embeddings with Vertex AI
- pgvector storage

### 🆕 Phase 2 Additions

#### What We're Adding:

1. **Identity Platform Authentication**
   - Google OAuth for customer sign-up
   - Public signup endpoint (no auth required)
   - Integration with existing Firebase Auth

2. **GCS Storage for Onboarding**
   - Private bucket: `anzx-user-onboarding`
   - Structured customer data storage
   - Secure with Uniform bucket-level access

3. **Public Provisioning API**
   - New router: `/api/v1/public` (unauthenticated)
   - Endpoints:
     - `POST /api/v1/public/signup` - Customer registration
     - `POST /api/v1/public/agents/provision` - Agent provisioning
     - `GET /api/v1/public/agents/:id/status` - Agent status

4. **Marketing Website Integration**
   - Next.js frontend (anzx-marketing)
   - "Hire Me" buttons on agent cards
   - Dynamic provisioning forms
   - Client libraries that call core-api

5. **Enhanced Monitoring**
   - Cloud Logging structured logs
   - Cloud Monitoring dashboard
   - Alerting policies
   - Usage event tracking

6. **CI/CD with Workload Identity**
   - GitHub Actions with WIF
   - No long-lived service account keys
   - Automated deployments

## Architecture Flow

```
Customer Browser
    ↓
anzx-marketing (Next.js) - NEW
    ↓ API calls
core-api (FastAPI) - EXISTING + NEW ENDPOINTS
    ↓
Existing Services:
- vertex_ai_service.py (Vertex AI Agent Builder)
- agent_service.py (Agent management)
- gcp_auth_service.py (Workload Identity)
- stripe_service.py (Billing)
    ↓
Google Cloud Platform:
- Vertex AI Agent Builder
- Cloud SQL (PostgreSQL + pgvector)
- GCS (anzx-user-onboarding) - NEW
- Cloud Logging & Monitoring
- Identity Platform - NEW
```

## What We're NOT Changing

✅ **Keep as-is:**
- Existing Vertex AI integration (`vertex_ai_service.py`)
- Existing agent management (`agent_service.py`)
- Existing database models and migrations
- Existing authentication system (Firebase Auth)
- Existing billing system (Stripe)
- Existing conversation management
- Existing knowledge service
- Existing agent orchestration

## What We're Adding/Modifying

### Backend (core-api)

**New Files:**
- `app/routers/public.py` - Public endpoints for customer provisioning
- `app/services/gcs_storage_service.py` - GCS operations
- `app/services/usage_events_service.py` - Usage event tracking
- `app/observability/cloud_logging.py` - Structured logging wrapper

**Modified Files:**
- `main.py` - Include new public router
- `requirements.txt` - Add `google-cloud-logging`

### Frontend (anzx-marketing)

**New Files:**
- `components/auth/GoogleSignUpForm.tsx` - Google OAuth sign-up
- `components/agents/AgentProvisioningModal.tsx` - Dynamic provisioning form
- `lib/google-cloud/agentspace-client.ts` - Calls core-api
- `lib/google-cloud/vertex-ai-client.ts` - Calls core-api
- `lib/google-cloud/mcp-config.ts` - Context management
- `lib/google-cloud/a2a-client.ts` - Agent linking
- `lib/google-cloud/workload-identity.ts` - CI/CD helper

**Modified Files:**
- `components/home/AnimatedAgentCard.tsx` - Add "Hire Me" button
- `app/[locale]/get-started/page.tsx` - Add sign-up form
- `lib/google-cloud/adk-templates.ts` - Complete agent schemas

### Infrastructure

**New Resources:**
- GCS bucket: `anzx-user-onboarding`
- Service account: `anzx-customer-provisioning`
- Workload Identity Pool: `github-actions-pool`
- Identity Platform configuration
- Cloud Monitoring dashboard
- Alerting policies

## Integration Points

### 1. Authentication Flow
```
Customer → Google OAuth (Identity Platform)
    ↓
anzx-marketing → POST /api/v1/public/signup
    ↓
core-api → Verify ID token → Create User/Org
    ↓
Return JWT token (existing auth system)
```

### 2. Provisioning Flow
```
Customer → Fill provisioning form
    ↓
anzx-marketing → POST /api/v1/public/agents/provision
    ↓
core-api → Write to GCS → Call agent_service.create_agent()
    ↓
agent_service → Call vertex_ai_service.create_agent()
    ↓
vertex_ai_service → Vertex AI Agent Builder
    ↓
Return agent details to customer
```

### 3. Status Monitoring
```
Customer → View agent dashboard
    ↓
anzx-marketing → GET /api/v1/public/agents/:id/status
    ↓
core-api → Query Assistant model → Get Vertex AI metrics
    ↓
Return status and metrics
```

## API Endpoint Mapping

### Existing Endpoints (Keep Using)
- `POST /api/v1/agents/` - Create agent (authenticated)
- `GET /api/v1/agents/:id` - Get agent details
- `POST /api/v1/agents/:id/chat` - Chat with agent
- `GET /api/v1/agents/:id/analytics` - Agent analytics

### New Public Endpoints (Phase 2)
- `POST /api/v1/public/signup` - Customer registration (no auth)
- `POST /api/v1/public/agents/provision` - Customer provisioning (no auth initially, then JWT)
- `GET /api/v1/public/agents/:id/status` - Agent status (public)

## Data Flow

### Customer Onboarding Data
```
GCS: gs://anzx-user-onboarding/users/{userId}/onboarding/{agentId}.json
{
  "userId": "...",
  "email": "...",
  "agentTemplateId": "olivia",
  "businessProfile": {...},
  "dataSources": [...],
  "requestedCapabilities": [...],
  "timestamp": "..."
}
```

### Agent Data (Existing)
```
PostgreSQL: assistants table
- id, name, type, organization_id
- model_config (includes vertex_ai_agent_id)
- tools_config, knowledge_sources
- deployment_status, version
```

## Security Model

### Existing Security (Keep)
- Firebase Auth for user authentication
- JWT tokens for API access
- Workload Identity for core-api → GCP
- IAM roles for service accounts
- TLS 1.2+ for all connections

### New Security (Phase 2)
- Identity Platform for customer sign-up
- GCS bucket with Uniform bucket-level access
- No public ACLs on customer data
- Workload Identity Federation for GitHub Actions
- Least-privilege IAM for new service account

## Testing Strategy

### Unit Tests
- Test new public endpoints
- Test GCS storage service
- Test provisioning logic
- Test authentication flow

### Integration Tests
- Test complete signup flow
- Test complete provisioning flow
- Test GCS operations
- Test Vertex AI integration (via existing tests)

### End-to-End Tests
- Test customer journey: browse → hire → provision
- Test agent status monitoring
- Test error scenarios

## Deployment Plan

### Phase 1: Infrastructure (Week 1)
1. Enable Identity Platform
2. Create GCS bucket with security settings
3. Create service account and IAM bindings
4. Configure Workload Identity Federation

### Phase 2: Backend (Weeks 2-3)
1. Add public router to core-api
2. Implement GCS storage service
3. Add Cloud Logging integration
4. Deploy updated core-api to Cloud Run
5. Test endpoints

### Phase 3: Frontend (Weeks 4-5)
1. Update agent templates
2. Create sign-up component
3. Add "Hire Me" buttons
4. Create provisioning modal
5. Implement client libraries

### Phase 4: Monitoring & CI/CD (Week 6)
1. Create monitoring dashboard
2. Set up alerting
3. Configure GitHub Actions with WIF
4. Deploy anzx-marketing to Cloud Run

### Phase 5: Testing & Launch (Weeks 7-9)
1. Integration testing
2. End-to-end testing
3. Security testing
4. Documentation
5. Production launch

## Success Metrics

- ✅ Customer can sign up in < 5 seconds
- ✅ Agent provisioning completes in < 30 seconds
- ✅ Provisioning success rate > 95%
- ✅ API response time < 500ms (p95)
- ✅ Zero long-lived keys in code/CI
- ✅ All customer data in private GCS bucket
- ✅ Complete audit trail in Cloud Logging

## Risk Mitigation

### Risk: Existing services disruption
**Mitigation:** All new code is additive, no changes to existing endpoints

### Risk: Authentication conflicts
**Mitigation:** Identity Platform integrates with existing Firebase Auth

### Risk: Performance impact
**Mitigation:** New endpoints are separate, won't affect existing traffic

### Risk: Security vulnerabilities
**Mitigation:** Security testing, least-privilege IAM, no public data access

## Next Steps

1. ✅ Review existing infrastructure (COMPLETE)
2. ⏳ Approve Phase 2 design and tasks
3. ⏳ Begin infrastructure setup
4. ⏳ Implement backend endpoints
5. ⏳ Build frontend integration
6. ⏳ Deploy and test

