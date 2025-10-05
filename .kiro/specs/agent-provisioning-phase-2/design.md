# Design Document: Real Agent Provisioning System

## Overview

This design document describes the architecture for Phase 2 of the ANZX AI platform, which enables customers to sign up via Google Identity Platform, hire specific AI agents through tailored forms, and have those agents automatically provisioned in Google Agentspace and deployed to Vertex AI Agent Engine. 

**Key Integration Point**: This phase builds on the existing backend infrastructure:
- **core-api** (FastAPI) - Already has Vertex AI integration, agent management, database models
- **agent-orchestration** - Hybrid agent orchestration system
- **knowledge-service** - Document processing and RAG capabilities

The marketing website (Next.js) will act as the customer-facing frontend that connects to these existing backend services through new API endpoints. The system emphasizes security through Workload Identity Federation, least-privilege IAM, and private GCS storage.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Customer Browser                         │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Agent Gallery  │  │ Hire Me Form │  │ Agent Dashboard   │  │
│  └────────────────┘  └──────────────┘  └───────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────┴──────────────────────────────────────┐
│              Next.js Marketing Site (anzx-marketing)             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Components: AnimatedAgentCard, GoogleSignUpForm,          │ │
│  │              AgentProvisioningFlow, AgentDashboard         │ │
│  │  Clients: agentspace-client.ts, vertex-ai-client.ts,       │ │
│  │           adk-templates.ts, mcp-config.ts, a2a-client.ts   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │ API Calls (REST/GraphQL)
┌──────────────────────────┴──────────────────────────────────────┐
│                  FastAPI Backend (core-api)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Existing Services:                                         │ │
│  │  - vertex_ai_service.py (Agent creation & deployment)      │ │
│  │  - agent_service.py (Agent management & conversations)     │ │
│  │  - hybrid_agent_orchestrator.py (Multi-agent routing)      │ │
│  │  - gcp_auth_service.py (Workload Identity)                 │ │
│  │  - stripe_service.py (Billing)                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  New Endpoints (Phase 2):                                   │ │
│  │  POST /api/v1/public/signup (Identity Platform auth)       │ │
│  │  POST /api/v1/public/agents/provision (Customer provision) │ │
│  │  GET  /api/v1/agents/:id/status (Agent health)             │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌───────▼────────┐ ┌──────▼──────┐
│ Identity       │ │ GCS Bucket     │ │ PostgreSQL  │
│ Platform       │ │ (private)      │ │ (Cloud SQL) │
│ (Google Auth)  │ │ anzx-user-     │ │ + pgvector  │
└────────────────┘ │ onboarding     │ └─────────────┘
                   └────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼─────────┐ ┌─────▼──────────┐
│ Cloud Logging  │  │ Cloud          │ │ Secret Manager │
│ & Monitoring   │  │ Monitoring     │ │ (API keys)     │
└────────────────┘  └────────────────┘ └────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                  Google Cloud Platform                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Vertex AI Agent Builder (via vertex_ai_service.py)        │ │
│  │  - Agent creation with templates                           │ │
│  │  - Conversation management                                 │ │
│  │  - Knowledge base integration                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Discovery Engine (Data Stores & Search)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
Customer → Click "Sign up with Google"
    ↓
Identity Platform → Google OAuth 2.0
    ↓
Google → User Consent Screen
    ↓
Identity Platform → ID Token (JWT)
    ↓
Next.js API → Verify ID Token
    ↓
Create Session → Store minimal profile
    ↓
Redirect to Agent Selection
```

### Provisioning Flow

```
Customer → Click "Hire Me" on Agent Card
    ↓
Check Auth → If not authenticated, redirect to /get-started
    ↓
Load Template → adk-templates.ts[agentId]
    ↓
Render Form → Dynamic fields based on template
    ↓
Customer → Fill form with business details
    ↓
Submit → POST /api/agents/provision
    ↓
Write to GCS → users/{userId}/onboarding/{agentId}.json
    ↓
agentspace-client.ts → createAgent(template, userCtx)
    ↓
Google Agentspace → Create agent instance → Return agentId
    ↓
vertex-ai-client.ts → deployAgent(agentId, region)
    ↓
Vertex AI Agent Engine → Deploy agent → Return deploymentId, endpoint
    ↓
mcp-config.ts → Save {userId, agentId, deploymentId, endpoint, contextConfig}
    ↓
(Optional) a2a-client.ts → linkAgents() if multi-agent
    ↓
Cloud Logging → Log provisioning success with deploymentId
    ↓
Return to Customer → Agent ready, show dashboard
```

## Components and Interfaces

### 1. Authentication Components

#### GoogleSignUpForm Component
**Location:** `services/anzx-marketing/components/auth/GoogleSignUpForm.tsx`

**Purpose:** Handles Google OAuth sign-in via Identity Platform

**Interface:**
```typescript
interface GoogleSignUpFormProps {
  preSelectedAgent?: string; // From URL param ?agent=emma
  onSuccess?: (user: User) => void;
}

interface User {
  uid: string;
  email: string;
  displayName: string;
  idToken: string;
}
```

**Behavior:**
- Renders "Sign up with Google" button
- Initiates Identity Platform OAuth flow
- Receives ID token from Google
- Sends token to `/api/signup` for verification
- Creates session and redirects to agent selection

#### Identity Platform Configuration
**Location:** Firebase/GCP Console + Environment Variables

**Required Setup:**
- Enable Identity Platform in GCP project
- Configure Google as identity provider
- Obtain Web Client ID and Client Secret
- Configure authorized redirect URIs

**Environment Variables:**
```bash
NEXT_PUBLIC_IDENTITY_PLATFORM_API_KEY=...
NEXT_PUBLIC_IDENTITY_PLATFORM_AUTH_DOMAIN=...
NEXT_PUBLIC_IDENTITY_PLATFORM_PROJECT_ID=...
```

### 2. Agent Selection Components

#### AnimatedAgentCard Component (Enhanced)
**Location:** `services/anzx-marketing/components/home/AnimatedAgentCard.tsx`

**Enhancements:**
- Add "Hire Me" button (primary CTA)
- Keep "Learn More" button (secondary)
- On "Hire Me" click:
  - Check authentication status
  - If not authenticated: redirect to `/get-started?agent={agentId}`
  - If authenticated: open provisioning modal

**Interface:**
```typescript
interface AnimatedAgentCardProps {
  agent: AgentTemplate;
  onHireClick: (agentId: string) => void;
  onLearnMoreClick: (agentId: string) => void;
}
```

#### AgentProvisioningModal Component
**Location:** `services/anzx-marketing/components/agents/AgentProvisioningModal.tsx`

**Purpose:** Dynamic form for agent-specific configuration

**Interface:**
```typescript
interface AgentProvisioningModalProps {
  agentTemplate: AgentTemplate;
  userId: string;
  onSubmit: (data: ProvisioningData) => Promise<void>;
  onCancel: () => void;
}

interface ProvisioningData {
  agentTemplateId: string;
  businessProfile: Record<string, any>;
  dataSources: DataSource[];
  requestedCapabilities: string[];
}
```

**Behavior:**
- Reads template from `adk-templates.ts`
- Dynamically renders form fields based on `template.requiredFields`
- Validates input based on template schema
- Submits to `/api/agents/provision`

### 3. Backend API Routes

#### POST /api/signup
**Location:** `services/anzx-marketing/app/api/signup/route.ts`

**Purpose:** Verify Identity Platform token and create user session

**Request:**
```typescript
{
  idToken: string;
  profile?: {
    company?: string;
    role?: string;
  }
}
```

**Response:**
```typescript
{
  success: boolean;
  userId: string;
  sessionToken: string;
}
```

**Implementation:**
1. Verify ID token using Identity Platform Admin SDK
2. Extract user info (uid, email, name)
3. Create minimal user record in database
4. Create secure session
5. Return session token

#### POST /api/agents/provision
**Location:** `services/anzx-marketing/app/api/agents/provision/route.ts`

**Purpose:** Orchestrate agent provisioning

**Request:**
```typescript
{
  agentTemplateId: string;
  businessProfile: {
    company: string;
    industry: string;
    useCase: string;
    // Template-specific fields
  };
  dataSources: Array<{
    type: string;
    config: Record<string, any>;
  }>;
  requestedCapabilities: string[];
}
```

**Response:**
```typescript
{
  success: boolean;
  agentId: string;
  deploymentId: string;
  endpoint: string;
  status: 'provisioning' | 'deployed' | 'failed';
}
```

**Implementation:**
1. Verify user authentication and authorization
2. Validate request against template schema
3. Write onboarding record to GCS
4. Call `agentspace-client.createAgent()`
5. Call `vertex-ai-client.deployAgent()`
6. Save config to `mcp-config.ts`
7. Log to Cloud Logging
8. Emit usage event
9. Return deployment details

#### GET /api/agents/:id/status
**Location:** `services/anzx-marketing/app/api/agents/[id]/status/route.ts`

**Purpose:** Get agent health and metrics

**Response:**
```typescript
{
  agentId: string;
  status: 'active' | 'inactive' | 'error';
  deploymentId: string;
  endpoint: string;
  metrics: {
    requestCount: number;
    avgLatency: number;
    errorRate: number;
  };
  lastActive: string;
}
```

### 4. Google Cloud Integration Clients

#### agentspace-client.ts
**Location:** `services/anzx-marketing/lib/google-cloud/agentspace-client.ts`

**Purpose:** Create and manage agents in Google Agentspace

**Key Functions:**
```typescript
async function createAgent(
  template: AgentTemplate,
  userContext: UserContext
): Promise<AgentCreationResult> {
  // 1. Authenticate with Agentspace API
  // 2. Prepare agent configuration from template
  // 3. Call Agentspace API to create agent
  // 4. Configure tools, policy packs, safety settings
  // 5. Return agentId
}

interface AgentCreationResult {
  agentId: string;
  name: string;
  status: string;
}
```

**API Reference:** [Google Agentspace Documentation](https://cloud.google.com/agentspace/docs)

**Authentication:** Uses Application Default Credentials or Workload Identity

#### vertex-ai-client.ts
**Location:** `services/anzx-marketing/lib/google-cloud/vertex-ai-client.ts`

**Purpose:** Deploy agents to Vertex AI Agent Engine

**Key Functions:**
```typescript
async function deployAgent(
  agentId: string,
  region: string,
  config?: DeploymentConfig
): Promise<DeploymentResult> {
  // 1. Authenticate with Vertex AI API
  // 2. Prepare deployment configuration
  // 3. Deploy agent to Agent Engine
  // 4. Implement retry with exponential backoff
  // 5. Return deploymentId and endpoint
}

interface DeploymentResult {
  deploymentId: string;
  endpoint: string;
  region: string;
  status: 'deploying' | 'deployed' | 'failed';
}
```

**API Reference:** [Vertex AI Agent Engine Documentation](https://cloud.google.com/vertex-ai/docs/agent-engine)

**Retry Logic:** Exponential backoff with jitter (1s, 2s, 4s, 8s, 16s max)

#### adk-templates.ts
**Location:** `services/anzx-marketing/lib/google-cloud/adk-templates.ts`

**Purpose:** Define agent templates with configuration schemas

**Interface:**
```typescript
interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  requiredFields: FieldDefinition[];
  tools: ToolConfig[];
  safety: SafetyConfig;
  defaultPromptStyle: string;
  dataConnectors: DataConnectorConfig[];
}

interface FieldDefinition {
  name: string;
  type: 'text' | 'email' | 'select' | 'multiselect' | 'textarea';
  label: string;
  required: boolean;
  options?: string[];
  validation?: ValidationRule;
}

const AGENT_TEMPLATES: Record<string, AgentTemplate> = {
  emma: {
    id: 'emma',
    name: 'Emma - AI Recruiting Agent',
    requiredFields: [
      { name: 'atsSystem', type: 'select', label: 'ATS System', required: true, options: ['Greenhouse', 'Lever', 'BambooHR'] },
      { name: 'hiringVolume', type: 'select', label: 'Monthly Hiring Volume', required: true, options: ['1-10', '11-50', '50+'] },
      { name: 'jobTypes', type: 'multiselect', label: 'Job Types', required: true, options: ['Engineering', 'Sales', 'Marketing', 'Operations'] }
    ],
    tools: ['resume_parser', 'calendar_integration', 'email_sender'],
    safety: { harmCategory: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' },
    defaultPromptStyle: 'professional_recruiter',
    dataConnectors: ['ats_api', 'calendar_api']
  },
  olivia: {
    id: 'olivia',
    name: 'Olivia - Customer Service AI',
    requiredFields: [
      { name: 'helpdeskSystem', type: 'select', label: 'Helpdesk System', required: true, options: ['Zendesk', 'Intercom', 'Freshdesk'] },
      { name: 'supportChannels', type: 'multiselect', label: 'Support Channels', required: true, options: ['Email', 'Chat', 'Phone'] },
      { name: 'ticketVolume', type: 'select', label: 'Monthly Ticket Volume', required: true, options: ['<100', '100-1000', '1000+'] }
    ],
    tools: ['ticket_manager', 'knowledge_base_search', 'sentiment_analyzer'],
    safety: { harmCategory: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_LOW_AND_ABOVE' },
    defaultPromptStyle: 'empathetic_support',
    dataConnectors: ['helpdesk_api', 'knowledge_base']
  },
  // ... other agents
};
```

#### mcp-config.ts
**Location:** `services/anzx-marketing/lib/google-cloud/mcp-config.ts`

**Purpose:** Persist conversation context configuration

**Interface:**
```typescript
interface MCPConfig {
  userId: string;
  agentId: string;
  deploymentId: string;
  endpoint: string;
  contextConfig: {
    contextWindow: number;
    groundingSources: string[];
    conversationStateStrategy: 'stateless' | 'session' | 'persistent';
  };
}

async function saveMCPConfig(config: MCPConfig): Promise<void>;
async function getMCPConfig(userId: string, agentId: string): Promise<MCPConfig | null>;
```

**Storage:** GCS bucket or Cloud Firestore for fast access

#### a2a-client.ts
**Location:** `services/anzx-marketing/lib/google-cloud/a2a-client.ts`

**Purpose:** Enable agent-to-agent communication

**Interface:**
```typescript
async function linkAgents(
  primaryId: string,
  secondaryId: string,
  mode: 'handoff' | 'collaboration' | 'escalation'
): Promise<LinkResult> {
  // 1. Validate both agents exist
  // 2. Register allowed cross-calls in config
  // 3. Set up message routing
  // 4. Return link configuration
}

interface LinkResult {
  linkId: string;
  primaryAgentId: string;
  secondaryAgentId: string;
  mode: string;
  status: 'active' | 'inactive';
}
```

#### workload-identity.ts
**Location:** `services/anzx-marketing/lib/google-cloud/workload-identity.ts`

**Purpose:** Helper for Workload Identity Federation

**Interface:**
```typescript
async function getGCPCredentials(
  githubToken?: string
): Promise<GoogleAuth> {
  // 1. If in GitHub Actions, use OIDC token
  // 2. Exchange for GCP credentials via Workload Identity
  // 3. Return authenticated client
  // 4. For local dev, use Application Default Credentials
}
```

**Configuration:**
```typescript
const WORKLOAD_IDENTITY_CONFIG = {
  projectNumber: process.env.GCP_PROJECT_NUMBER,
  poolId: 'github-actions-pool',
  providerId: 'github-provider',
  serviceAccount: 'github-actions@anzx-ai-platform.iam.gserviceaccount.com'
};
```

## Data Models

### Onboarding Record (GCS)
**Path:** `gs://anzx-user-onboarding/users/{userId}/onboarding/{agentTemplateId}.json`

```json
{
  "userId": "user_abc123",
  "email": "customer@company.com",
  "agentTemplateId": "olivia",
  "businessProfile": {
    "company": "Acme Corp",
    "industry": "SaaS",
    "useCase": "Automate customer support for 1000+ monthly tickets",
    "helpdeskSystem": "Zendesk",
    "supportChannels": ["Email", "Chat"],
    "ticketVolume": "1000+"
  },
  "dataSources": [
    {
      "type": "zendesk_api",
      "config": {
        "subdomain": "acme",
        "apiTokenSecretId": "projects/anzx-ai-platform/secrets/acme-zendesk-token"
      }
    },
    {
      "type": "knowledge_base",
      "config": {
        "gcsPath": "gs://acme-knowledge-base/docs/"
      }
    }
  ],
  "requestedCapabilities": [
    "ticket_routing",
    "sentiment_analysis",
    "auto_response"
  ],
  "timestamp": "2025-05-10T10:30:00Z",
  "status": "pending_provisioning"
}
```

### MCP Configuration
**Storage:** Cloud Firestore collection `mcp_configs`

```json
{
  "userId": "user_abc123",
  "agentId": "agent_xyz789",
  "deploymentId": "deployment_123",
  "endpoint": "https://us-central1-aiplatform.googleapis.com/v1/projects/anzx-ai-platform/locations/us-central1/endpoints/deployment_123",
  "contextConfig": {
    "contextWindow": 8192,
    "groundingSources": [
      "gs://acme-knowledge-base/docs/",
      "zendesk://acme.zendesk.com/articles"
    ],
    "conversationStateStrategy": "persistent"
  },
  "createdAt": "2025-05-10T10:35:00Z",
  "updatedAt": "2025-05-10T10:35:00Z"
}
```

## Error Handling

### Authentication Errors
- **Invalid ID Token:** Return 401 with message "Authentication failed"
- **Expired Token:** Return 401 with message "Session expired, please sign in again"
- **Missing Permissions:** Return 403 with message "Insufficient permissions"

### Provisioning Errors
- **Template Not Found:** Return 400 with message "Invalid agent template"
- **Validation Failed:** Return 400 with detailed field errors
- **Agentspace API Error:** Retry with exponential backoff, log error, return 503 if all retries fail
- **Vertex AI Deployment Error:** Retry with exponential backoff, log error, return 503 if all retries fail
- **GCS Write Error:** Log error, return 500 with message "Failed to save configuration"

### Retry Strategy
```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 5,
  baseDelay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Testing Strategy

### Unit Tests
- Test each client function in isolation with mocked GCP APIs
- Test form validation logic
- Test retry logic with simulated failures
- Test token verification

### Integration Tests
- Test full provisioning flow with test GCP project
- Test authentication flow with test Identity Platform
- Test GCS writes and reads
- Test Workload Identity Federation locally

### End-to-End Tests
- Test complete user journey: sign up → hire agent → provision → verify deployment
- Test error scenarios and recovery
- Test multi-agent provisioning
- Test A2A communication

### Security Tests
- Verify no long-lived keys in code or environment
- Verify IAM permissions are least-privilege
- Verify GCS bucket has no public access
- Verify ID token validation is secure

## Security Considerations

### IAM Roles

**Service Account for Application:**
- `roles/storage.objectCreator` on `anzx-user-onboarding` bucket
- `roles/storage.objectViewer` on `anzx-user-onboarding` bucket
- `roles/aiplatform.user` for Vertex AI operations
- `roles/logging.logWriter` for Cloud Logging

**Service Account for GitHub Actions:**
- `roles/run.developer` for Cloud Run deployments
- `roles/storage.objectAdmin` for build artifacts
- `roles/iam.workloadIdentityUser` for Workload Identity

### GCS Bucket Security
- **Uniform bucket-level access:** Enabled
- **Public access:** Disabled (no `allUsers` or `allAuthenticatedUsers`)
- **Object ownership:** Service account only
- **Encryption:** Google-managed (with CMEK stubs for future)
- **Versioning:** Enabled for data recovery
- **Lifecycle:** Retain for 90 days, then archive

### Secrets Management
- **API Keys:** Store in Secret Manager, reference by secret ID
- **Service Account Keys:** Use Workload Identity, no keys in code
- **Customer Credentials:** Encrypt before storing, use Secret Manager

### Network Security
- **HTTPS Only:** All API endpoints require HTTPS
- **CORS:** Restrict to anzx.ai domain
- **Rate Limiting:** Implement per-user rate limits
- **DDoS Protection:** Use Cloud Armor

## Monitoring and Observability

### Cloud Logging
**Log Structure:**
```json
{
  "severity": "INFO",
  "timestamp": "2025-05-10T10:30:00Z",
  "trace": "projects/anzx-ai-platform/traces/abc123",
  "spanId": "xyz789",
  "labels": {
    "userId": "user_abc123",
    "agentId": "agent_xyz789",
    "operation": "provision_agent"
  },
  "jsonPayload": {
    "message": "Agent provisioned successfully",
    "deploymentId": "deployment_123",
    "duration_ms": 5432
  }
}
```

**Key Events to Log:**
- User sign-up
- Agent selection
- Provisioning start
- Agentspace agent creation
- Vertex AI deployment
- Provisioning complete
- API errors
- Retry attempts

### Cloud Monitoring
**Dashboard Metrics:**
- Provisioning success rate
- Provisioning duration (p50, p95, p99)
- API request count by endpoint
- API error rate by endpoint
- Vertex AI agent request count
- Vertex AI agent latency
- GCS bucket operations

**Alerting Policies:**
- Provisioning failure rate > 5%
- API error rate > 1%
- Vertex AI latency > 2s (p95)
- GCS bucket quota > 80%

### Usage Events
**Event Structure:**
```typescript
interface UsageEvent {
  userId: string;
  agentId: string;
  timestamp: string;
  eventType: 'api_call' | 'conversation' | 'token_usage';
  metadata: {
    requestId?: string;
    tokenCount?: number;
    duration_ms?: number;
  };
}
```

**Emission Points:**
- Every Vertex AI API call
- Every conversation turn
- Every token processed
- Every data connector invocation

## Deployment Architecture

### CI/CD with Workload Identity Federation

**GitHub Actions Workflow:**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for OIDC
    
    steps:
      - uses: actions/checkout@v3
      
      - id: auth
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider'
          service_account: 'github-actions@anzx-ai-platform.iam.gserviceaccount.com'
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy anzx-marketing \
            --source . \
            --region us-central1 \
            --platform managed
```

**Workload Identity Setup:**
```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-actions-pool \
  --location=global \
  --display-name="GitHub Actions Pool"

# Create Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-actions-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"

# Grant IAM binding
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@anzx-ai-platform.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/anzx-ai/anzx-platform"
```

## Performance Considerations

### Provisioning Performance
- **Target:** < 30 seconds from form submit to agent deployed
- **Optimization:** Parallel execution of Agentspace and Vertex AI calls where possible
- **Caching:** Cache agent templates and configurations

### API Performance
- **Target:** < 200ms for authentication endpoints
- **Target:** < 500ms for status endpoints
- **Optimization:** Use Cloud CDN for static assets
- **Optimization:** Implement response caching with appropriate TTLs

### Scalability
- **Horizontal Scaling:** Cloud Run auto-scales based on request volume
- **Database:** Use Cloud Firestore for low-latency config access
- **Rate Limiting:** 100 requests/minute per user for provisioning

## Future Enhancements

1. **Multi-Region Deployment:** Deploy agents to customer-preferred regions
2. **Custom Models:** Allow customers to fine-tune models with their data
3. **Advanced A2A:** Implement complex multi-agent workflows with orchestration
4. **Real-Time Monitoring:** WebSocket-based live agent monitoring
5. **Cost Optimization:** Automatic scaling down of idle agents
6. **Compliance:** SOC 2, HIPAA, GDPR compliance certifications

