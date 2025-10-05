# Implementation Plan: Real Agent Provisioning (Phase 2)

## Overview

This phase connects the ANZX marketing website (anzx.ai) to the existing production backend services, enabling customers to sign up, hire agents, and have them provisioned automatically. The backend infrastructure (core-api, agent-orchestration, knowledge-service) is already deployed on Cloud Run with Vertex AI integration.

## ⚠️ CRITICAL CONSTRAINTS

### 1. **DO NOT BREAK EXISTING MARKETING WEBSITE**
- The current anzx.ai marketing website MUST continue working
- All new features are ADDITIVE ONLY
- No changes to existing pages unless explicitly adding new components
- Test existing pages after every change
- Use feature flags if needed to toggle new functionality

### 2. **USE EXISTING DEPLOYED COMPONENTS**
- ✅ **core-api** (FastAPI) - Already deployed on Cloud Run
  - Use existing routers: `/api/v1/auth`, `/api/v1/agents`, `/api/v1/organizations`, etc.
  - Use existing services: `vertex_ai_service.py`, `agent_service.py`, `gcp_auth_service.py`
  - Use existing database models and migrations
- ✅ **agent-orchestration** - Already deployed
- ✅ **knowledge-service** - Already deployed
- ✅ **PostgreSQL + pgvector** - Already configured
- ✅ **Stripe billing** - Already integrated
- ✅ **Firebase Auth** - Already working

### 3. **REVIEW END-TO-END CODE**
- Before implementing ANY task, review existing code in the repository
- Check for existing implementations that can be reused
- Verify integration points with existing services
- Test against deployed services, not mocks
- Document any assumptions about existing code

### 4. **BACKWARD COMPATIBILITY**
- New API endpoints must not conflict with existing ones
- New database migrations must be backward compatible
- New environment variables must have defaults
- Existing functionality must continue to work during rollout

## Architecture Integration

**Existing Infrastructure (Already Deployed):**
- ✅ **core-api** (FastAPI) - Cloud Run, australia-southeast1
  - Vertex AI Agent Builder integration (`vertex_ai_service.py`)
  - Agent management (`agent_service.py`)
  - Workload Identity authentication (`gcp_auth_service.py`)
  - PostgreSQL + pgvector for data storage
  - Stripe billing integration
- ✅ **agent-orchestration** - Hybrid agent routing
- ✅ **knowledge-service** - Document processing & RAG

**New Phase 2 Work:**
- Marketing website customer-facing flows
- Public API endpoints for customer provisioning
- GCS storage for onboarding data
- Integration between Next.js frontend and FastAPI backend

---

## Pre-Implementation Checklist

Before starting ANY task, complete this checklist:

- [-] **Review existing code** in the repository for the component you're modifying
- [ ] **Check for existing implementations** that can be reused
- [ ] **Verify integration points** with deployed services
- [ ] **Test existing functionality** before making changes
- [ ] **Document assumptions** about existing code behavior
- [ ] **Create feature branch** from main/master
- [ ] **Set up local development** environment matching production
- [ ] **Verify access** to GCP project `extreme-gecko-466211-t1`
- [ ] **Test against deployed services** (core-api on Cloud Run)
- [ ] **Have rollback plan** ready

## Implementation Tasks

**Recommended Implementation Order:**
1. Infrastructure & IAM (Tasks 1-3) - Foundation
2. Agent Templates (Task 8) - Define schemas first
3. Backend Services (Tasks 7, 18, 21) - Core services
4. Backend API Endpoints (Tasks 4-6) - Public APIs
5. Frontend Components (Tasks 9-12) - UI integration
6. Client Libraries (Tasks 13-17) - API wrappers
7. Monitoring & CI/CD (Tasks 19-20, 22-24) - Observability
8. Testing & Documentation (Tasks 25-28) - Quality assurance

---

### Phase 2.1: Infrastructure Setup (Foundation)

- [ ] 1. Set up Google Identity Platform for customer authentication
  - [ ] 1.1 Enable Identity Platform API in GCP project `extreme-gecko-466211-t1`
  - [ ] 1.2 Configure Google as identity provider with OAuth 2.0
  - [ ] 1.3 Obtain Web Client ID and Client Secret for anzx.ai domain
  - [ ] 1.4 Configure authorized redirect URIs for production and development
  - [ ] 1.5 Set up Identity Platform Admin SDK in core-api for token verification
  - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - _Reference: https://cloud.google.com/identity-platform/docs/web/google_

- [ ] 2. Create secure GCS bucket for customer onboarding data
  - [ ] 2.1 Create GCS bucket `anzx-user-onboarding` in australia-southeast1
  - [ ] 2.2 Enable Uniform bucket-level access (disable ACLs)
  - [ ] 2.3 Remove all public access (no `allUsers` or `allAuthenticatedUsers`)
  - [ ] 2.4 Configure bucket ownership to dedicated service account
  - [ ] 2.5 Enable versioning for data recovery
  - [ ] 2.6 Set up lifecycle policy (retain 90 days, then archive)
  - [ ] 2.7 Add CMEK encryption configuration stubs for future use
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  - _Reference: https://cloud.google.com/storage/docs/uniform-bucket-level-access_

- [ ] 3. Configure IAM roles and service accounts
  - [ ] 3.1 Create service account `anzx-customer-provisioning@extreme-gecko-466211-t1.iam.gserviceaccount.com`
  - [ ] 3.2 Grant `roles/storage.objectCreator` on `anzx-user-onboarding` bucket
  - [ ] 3.3 Grant `roles/storage.objectViewer` on `anzx-user-onboarding` bucket
  - [ ] 3.4 Grant `roles/aiplatform.user` for Vertex AI operations
  - [ ] 3.5 Grant `roles/logging.logWriter` for Cloud Logging
  - [ ] 3.6 Document all IAM bindings in runbook
  - _Requirements: 2.8, 11.1, 11.2_
  - _Reference: https://cloud.google.com/iam/docs/best-practices_

### Phase 2.2: Agent Templates & Core Services (Prerequisites)

- [ ] 4. Define agent template schemas (MUST DO FIRST)
  - [ ] 4.1 Expand `lib/google-cloud/adk-templates.ts` with complete agent schemas
  - [ ] 4.2 Define `AgentTemplate` interface with requiredFields, tools, safety, dataConnectors
  - [ ] 4.3 Create template for Emma (recruiting): ATS system, hiring volume, job types
  - [ ] 4.4 Create template for Olivia (customer service): helpdesk, channels, ticket volume
  - [ ] 4.5 Create template for Jack (sales): CRM system, lead sources, sales process
  - [ ] 4.6 Create templates for Inder, Alex, Ashish, Liam with specific fields
  - [ ] 4.7 Export templates for use in provisioning forms
  - [ ] 4.8 Validate template schemas with JSON Schema
  - _Requirements: 9.1, 9.2, 9.3_
  - _File: `services/anzx-marketing/lib/google-cloud/adk-templates.ts`_
  - _Note: This MUST be done before backend validation (Task 8.2)_

- [ ] 5. Add GCS storage service to core-api
  - [ ] 5.1 Create `app/services/gcs_storage_service.py`
  - [ ] 5.2 Implement `write_onboarding_record()` method
  - [ ] 5.3 Implement `read_onboarding_record()` method
  - [ ] 5.4 Use existing `gcp_auth_service.py` for authentication
  - [ ] 5.5 Add structured metadata to GCS objects
  - [ ] 5.6 Implement error handling and logging
  - _Requirements: 2.1, 2.2, 2.3_
  - _Integrates with: Existing `gcp_auth_service.py`_
  - _Note: Required by Task 8.3_

- [ ] 6. Implement Cloud Logging integration
  - [ ] 6.1 Add `@google-cloud/logging` to core-api dependencies
  - [ ] 6.2 Create `app/observability/cloud_logging.py` wrapper
  - [ ] 6.3 Log structured JSON with trace IDs and span IDs
  - [ ] 6.4 Log key events: signup, agent selection, provisioning start/complete
  - [ ] 6.5 Include user context in logs (userId, organizationId, agentId)
  - [ ] 6.6 Set up log-based metrics in Cloud Monitoring
  - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - _Reference: https://cloud.google.com/logging/docs/setup/python_
  - _Note: Set up early for debugging_

- [ ] 7. Implement usage event emitter
  - [ ] 7.1 Create `app/services/usage_events_service.py`
  - [ ] 7.2 Define `UsageEvent` model with event types
  - [ ] 7.3 Emit events for: API calls, conversations, token usage
  - [ ] 7.4 Write events to BigQuery for billing analysis
  - [ ] 7.5 Integrate with existing Stripe billing service
  - _Requirements: 7.1, 7.2, 7.3_
  - _Integrates with: Existing `stripe_service.py`, `usage_tracking.py`_
  - _Note: Required by Task 8.6_

### Phase 2.3: Backend API Endpoints (core-api)

- [ ] 8. Create public signup endpoint in core-api
  - [ ] 8.1 Create new router `app/routers/public.py` for unauthenticated endpoints
  - [ ] 8.2 Implement `POST /api/v1/public/signup` endpoint
  - [ ] 8.3 Verify Identity Platform ID token using Admin SDK
  - [ ] 8.4 Extract user info (uid, email, name) from verified token
  - [ ] 8.5 Create or update User record in PostgreSQL
  - [ ] 8.6 Create Organization record if new customer
  - [ ] 8.7 Return JWT access token for subsequent requests
  - [ ] 8.8 Log signup event to Cloud Logging with structured data
  - _Requirements: 1.1, 1.2, 1.3, 12.1_
  - _Integrates with: Existing `auth/firebase.py`, `models/user.py`_
  - _Depends on: Task 6 (Cloud Logging)_

- [ ] 9. Create customer provisioning endpoint
  - [ ] 9.1 Implement `POST /api/v1/public/agents/provision` endpoint
  - [ ] 9.2 Validate request against agent template schema from `adk-templates.ts` (Task 4)
  - [ ] 9.3 Write onboarding record to GCS using `gcs_storage_service` (Task 5)
  - [ ] 9.4 Call existing `agent_service.create_agent()` with customer data
  - [ ] 9.5 Return agent details: agentId, deploymentId, endpoint, status
  - [ ] 9.6 Emit usage event using `usage_events_service` (Task 7)
  - [ ] 9.7 Send admin notification email to inderanz@gmail.com
  - [ ] 9.8 Implement retry logic with exponential backoff for Vertex AI calls
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - _Integrates with: Existing `agent_service.py`, `vertex_ai_service.py`_
  - _Depends on: Tasks 4, 5, 6, 7_

- [ ] 10. Create agent status endpoint
  - [ ] 10.1 Implement `GET /api/v1/public/agents/:id/status` endpoint
  - [ ] 10.2 Query Assistant model from PostgreSQL
  - [ ] 10.3 Fetch Vertex AI metrics using existing `vertex_ai_service.get_agent_metrics()`
  - [ ] 10.4 Return health status, metrics, and deployment info
  - [ ] 10.5 Cache response for 30 seconds to reduce API calls
  - _Requirements: 12.1, 12.2_
  - _Integrates with: Existing `agent_service.py`, `vertex_ai_service.py`_

- [ ] 11. Update main.py to include public router
  - [ ] 11.1 Import public router in `main.py`
  - [ ] 11.2 Add `app.include_router(public.router)` to router list
  - [ ] 11.3 **CRITICAL:** Test ALL existing endpoints still work (auth, agents, organizations, billing)
  - [ ] 11.4 Test new public endpoints with curl/Postman
  - [ ] 11.5 Run existing test suite to ensure no regressions
  - [ ] 11.6 Deploy updated core-api to Cloud Run
  - [ ] 11.7 Verify all endpoints (existing + new) are accessible in production
  - [ ] 11.8 Monitor logs for any errors after deployment
  - _Depends on: Tasks 8, 9, 10_
  - _⚠️ MUST NOT break existing API endpoints_

### Phase 2.4: Frontend Integration (anzx-marketing)

- [ ] 12. Create Google Identity sign-up component
  - [ ] 12.1 Create `components/auth/GoogleSignUpForm.tsx`
  - [ ] 12.2 Integrate Identity Platform Web SDK
  - [ ] 12.3 Implement "Sign up with Google" button with OAuth flow
  - [ ] 12.4 Handle ID token reception and verification
  - [ ] 12.5 Call `POST /api/v1/public/signup` with ID token (Task 8)
  - [ ] 12.6 Store JWT access token in secure httpOnly cookie
  - [ ] 12.7 Handle authentication errors gracefully
  - [ ] 12.8 Support pre-selected agent via URL parameter `?agent=emma`
  - _Requirements: 1.1, 1.2, 1.3_
  - _File: `services/anzx-marketing/components/auth/GoogleSignUpForm.tsx`_
  - _Depends on: Task 8 (signup endpoint)_

- [ ] 13. Update agent cards with "Hire Me" buttons
  - [ ] 13.1 **CRITICAL:** Review existing `AnimatedAgentCard.tsx` implementation first
  - [ ] 13.2 Update `components/home/AnimatedAgentCard.tsx` (ADDITIVE ONLY)
  - [ ] 13.3 Add "Hire Me" button as primary CTA
  - [ ] 13.4 Keep "Learn More" button as secondary CTA (MUST NOT REMOVE)
  - [ ] 13.5 On "Hire Me" click: check authentication status
  - [ ] 13.6 If not authenticated: redirect to `/get-started?agent={agentId}`
  - [ ] 13.7 If authenticated: open provisioning modal
  - [ ] 13.8 Add hover animations and visual feedback
  - [ ] 13.9 **CRITICAL:** Test existing agent card functionality still works
  - [ ] 13.10 Verify no visual regressions on homepage
  - _Requirements: 3.1, 3.2_
  - _File: `services/anzx-marketing/components/home/AnimatedAgentCard.tsx`_
  - _⚠️ MUST NOT break existing agent card display or interactions_

- [ ] 14. Create agent provisioning modal
  - [ ] 14.1 Create `components/agents/AgentProvisioningModal.tsx`
  - [ ] 14.2 Load agent template from `adk-templates.ts` (Task 4)
  - [ ] 14.3 Dynamically render form fields based on template.requiredFields
  - [ ] 14.4 Implement field validation based on template schema
  - [ ] 14.5 Collect business profile, data sources, requested capabilities
  - [ ] 14.6 Submit to `POST /api/v1/public/agents/provision` (Task 9)
  - [ ] 14.7 Show provisioning progress with loading states
  - [ ] 14.8 Display success message with agent details
  - [ ] 14.9 Handle errors and show user-friendly messages
  - _Requirements: 3.1, 3.2, 3.3, 9.1, 9.2_
  - _File: `services/anzx-marketing/components/agents/AgentProvisioningModal.tsx`_
  - _Depends on: Tasks 4, 9_

- [ ] 15. Update /get-started page
  - [ ] 15.1 **CRITICAL:** Review existing `/get-started` page implementation first
  - [ ] 15.2 Check if page has any existing functionality that must be preserved
  - [ ] 15.3 Update `app/[locale]/get-started/page.tsx` (preserve existing layout/styling)
  - [ ] 15.4 Replace placeholder content with GoogleSignUpForm
  - [ ] 15.5 Handle `?agent=` URL parameter for pre-selection
  - [ ] 15.6 Show agent-specific messaging based on pre-selection
  - [ ] 15.7 Redirect to provisioning flow after successful sign-up
  - [ ] 15.8 **CRITICAL:** Test page loads correctly without errors
  - [ ] 15.9 Verify internationalization (i18n) still works if implemented
  - _Requirements: 1.1, 3.1_
  - _File: `services/anzx-marketing/app/[locale]/get-started/page.tsx`_
  - _Depends on: Task 12_
  - _⚠️ MUST NOT break existing page routing or layout_

### Phase 2.5: Client Libraries (anzx-marketing)

- [ ] 16. Implement agentspace-client.ts
  - [ ] 16.1 Create `lib/google-cloud/agentspace-client.ts`
  - [ ] 16.2 Implement `createAgent()` function that calls core-api
  - [ ] 16.3 Implement `getAgentStatus()` function
  - [ ] 16.4 Implement `updateAgentConfig()` function
  - [ ] 16.5 Add TypeScript interfaces for requests/responses
  - [ ] 16.6 Implement error handling and retry logic
  - [ ] 16.7 Add request/response logging
  - _Requirements: 4.1, 4.2, 4.3_
  - _Note: Calls core-api endpoints, not direct GCP APIs_
  - _Depends on: Tasks 9, 10_

- [ ] 17. Implement vertex-ai-client.ts
  - [ ] 17.1 Create `lib/google-cloud/vertex-ai-client.ts`
  - [ ] 17.2 Implement `deployAgent()` function that calls core-api
  - [ ] 17.3 Implement `getDeploymentStatus()` function
  - [ ] 17.4 Add exponential backoff retry logic
  - [ ] 17.5 Add TypeScript interfaces for deployment results
  - [ ] 17.6 Implement error handling
  - _Requirements: 4.4, 4.5, 4.6_
  - _Note: Calls core-api endpoints, not direct GCP APIs_
  - _Depends on: Tasks 9, 10_

- [ ] 18. Implement mcp-config.ts
  - [ ] 18.1 Create `lib/google-cloud/mcp-config.ts`
  - [ ] 18.2 Define `MCPConfig` interface with context configuration
  - [ ] 18.3 Implement `saveMCPConfig()` function
  - [ ] 18.4 Implement `getMCPConfig()` function
  - [ ] 18.5 Store configs in localStorage for client-side caching
  - [ ] 18.6 Sync with backend via API calls
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 19. Implement a2a-client.ts
  - [ ] 19.1 Create `lib/google-cloud/a2a-client.ts`
  - [ ] 19.2 Implement `linkAgents()` function for agent collaboration
  - [ ] 19.3 Define link modes: handoff, collaboration, escalation
  - [ ] 19.4 Add TypeScript interfaces for A2A configuration
  - [ ] 19.5 Implement validation for agent linking
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 20. Implement workload-identity.ts helper
  - [ ] 20.1 Create `lib/google-cloud/workload-identity.ts`
  - [ ] 20.2 Document Workload Identity Federation setup
  - [ ] 20.3 Provide helper functions for local development
  - [ ] 20.4 Add configuration examples for GitHub Actions
  - _Requirements: 8.1, 8.2, 8.3_
  - _Note: Primarily documentation and CI/CD configuration_

### Phase 2.6: Monitoring & Observability

- [ ] 21. Create Cloud Monitoring dashboard
  - [ ] 21.1 Create dashboard JSON configuration
  - [ ] 21.2 Add widget for provisioning success rate
  - [ ] 21.3 Add widget for provisioning duration (p50, p95, p99)
  - [ ] 21.4 Add widget for API request count by endpoint
  - [ ] 21.5 Add widget for Vertex AI agent metrics
  - [ ] 21.6 Add widget for GCS bucket operations
  - [ ] 21.7 Deploy dashboard via Terraform or gcloud CLI
  - _Requirements: 6.5, 6.6, 6.7_
  - _Reference: https://cloud.google.com/monitoring/dashboards_
  - _Depends on: Task 6 (Cloud Logging)_

- [ ] 22. Set up alerting policies
  - [ ] 22.1 Create alert for provisioning failure rate > 5%
  - [ ] 22.2 Create alert for API error rate > 1%
  - [ ] 22.3 Create alert for Vertex AI latency > 2s (p95)
  - [ ] 22.4 Create alert for GCS bucket quota > 80%
  - [ ] 22.5 Configure notification channels (email, Slack)
  - _Requirements: 6.7_
  - _Reference: https://cloud.google.com/monitoring/alerts_
  - _Depends on: Task 21 (Dashboard)_

### Phase 2.7: CI/CD & Deployment

- [ ] 23. Configure Workload Identity Federation for GitHub Actions
  - [ ] 23.1 Create Workload Identity Pool: `github-actions-pool`
  - [ ] 23.2 Create OIDC Provider: `github-provider` with GitHub issuer
  - [ ] 23.3 Configure attribute mapping: `assertion.repository` → `attribute.repository`
  - [ ] 23.4 Create service account: `github-actions@extreme-gecko-466211-t1.iam.gserviceaccount.com`
  - [ ] 23.5 Grant `roles/iam.workloadIdentityUser` to service account
  - [ ] 23.6 Grant `roles/run.developer` for Cloud Run deployments
  - [ ] 23.7 Document pool/provider configuration in runbook
  - _Requirements: 8.1, 8.2, 8.3, 8.4_
  - _Reference: https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines_

- [ ] 24. Update GitHub Actions workflow
  - [ ] 24.1 Update `.github/workflows/deploy-production.yml`
  - [ ] 24.2 Add `id-token: write` permission for OIDC
  - [ ] 24.3 Use `google-github-actions/auth@v1` with Workload Identity
  - [ ] 24.4 Remove any long-lived service account keys from secrets
  - [ ] 24.5 Deploy anzx-marketing to Cloud Run
  - [ ] 24.6 Run integration tests after deployment
  - _Requirements: 8.1, 8.2, 8.3_
  - _Depends on: Task 23_

- [ ] 25. Deploy anzx-marketing to Cloud Run
  - [ ] 25.1 **CRITICAL:** Review existing anzx-marketing deployment configuration
  - [ ] 25.2 Check if Dockerfile already exists and reuse it
  - [ ] 25.3 Create or update Dockerfile for Next.js production build
  - [ ] 25.4 Build and push image to Artifact Registry
  - [ ] 25.5 **CRITICAL:** Deploy to staging environment FIRST for testing
  - [ ] 25.6 Test ALL existing pages work in staging (homepage, about, pricing, etc.)
  - [ ] 25.7 Test new functionality in staging
  - [ ] 25.8 Deploy to production Cloud Run in australia-southeast1
  - [ ] 25.9 Configure custom domain: anzx.ai (if not already configured)
  - [ ] 25.10 Verify SSL certificate with Cloud Load Balancer
  - [ ] 25.11 Configure environment variables for production
  - [ ] 25.12 Set up Cloud CDN for static assets (if not already configured)
  - [ ] 25.13 **CRITICAL:** Monitor production for 1 hour after deployment
  - [ ] 25.14 Have rollback plan ready in case of issues
  - _Requirements: 13.1, 13.2_
  - _Depends on: Tasks 11, 24_
  - _⚠️ MUST NOT break existing marketing website - test thoroughly in staging first_

### Phase 2.8: Testing & Documentation

- [ ] 26. Create comprehensive documentation
  - [ ] 26.1 Document all API endpoints with request/response examples
  - [ ] 26.2 Document required IAM roles for each component
  - [ ] 26.3 Document GCS bucket structure and data format
  - [ ] 26.4 Create runbook for provisioning flow
  - [ ] 26.5 Document troubleshooting procedures
  - [ ] 26.6 Create deployment guide with step-by-step instructions
  - [ ] 26.7 Reference official Google Cloud documentation
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 27. Write integration tests
  - [ ] 27.1 Test complete signup flow: Google OAuth → JWT token
  - [ ] 27.2 Test agent provisioning flow: form submit → agent deployed
  - [ ] 27.3 Test GCS write/read operations
  - [ ] 27.4 Test Vertex AI agent creation via core-api
  - [ ] 27.5 Test error scenarios and retry logic
  - [ ] 27.6 Test authentication failures and edge cases
  - _Requirements: 12.1, 12.2, 12.3_
  - _Depends on: Tasks 8, 9, 10, 11_

- [ ] 28. Write end-to-end tests
  - [ ] 28.1 Test complete user journey: browse → hire → provision → deployed
  - [ ] 28.2 Test multi-agent provisioning
  - [ ] 28.3 Test agent status monitoring
  - [ ] 28.4 Test A2A agent linking
  - [ ] 28.5 Run tests in staging environment
  - _Requirements: 12.1, 12.2, 12.3_
  - _Depends on: Tasks 12-15, 25_

- [ ] 29. Security testing
  - [ ] 29.1 Verify no long-lived keys in code or environment
  - [ ] 29.2 Verify IAM permissions are least-privilege
  - [ ] 29.3 Verify GCS bucket has no public access
  - [ ] 29.4 Verify ID token validation is secure
  - [ ] 29.5 Run OWASP ZAP security scan
  - [ ] 29.6 Perform penetration testing
  - _Requirements: 11.1, 11.2, 11.3, 11.4_
  - _Depends on: All previous tasks_

---

## File Structure

```
services/anzx-marketing/                    # Next.js marketing website
├── app/
│   ├── [locale]/
│   │   └── get-started/
│   │       └── page.tsx                   # Updated with sign-up form
│   └── api/                                # API routes (proxy to core-api)
│       └── proxy/
│           └── [...path]/route.ts         # Proxy to core-api
├── components/
│   ├── auth/
│   │   └── GoogleSignUpForm.tsx           # NEW: Google OAuth sign-up
│   ├── agents/
│   │   └── AgentProvisioningModal.tsx     # NEW: Dynamic provisioning form
│   └── home/
│       └── AnimatedAgentCard.tsx          # UPDATED: Add "Hire Me" button
├── lib/
│   └── google-cloud/
│       ├── agentspace-client.ts           # NEW: Calls core-api
│       ├── vertex-ai-client.ts            # NEW: Calls core-api
│       ├── adk-templates.ts               # UPDATED: Complete schemas
│       ├── mcp-config.ts                  # NEW: Context management
│       ├── a2a-client.ts                  # NEW: Agent linking
│       └── workload-identity.ts           # NEW: CI/CD helper
└── .env.production                        # Production environment variables

services/core-api/                          # FastAPI backend (existing)
├── app/
│   ├── routers/
│   │   ├── public.py                      # NEW: Public endpoints
│   │   ├── agents.py                      # EXISTING: Agent management
│   │   └── auth.py                        # EXISTING: Authentication
│   ├── services/
│   │   ├── gcs_storage_service.py         # NEW: GCS operations
│   │   ├── usage_events_service.py        # NEW: Usage tracking
│   │   ├── vertex_ai_service.py           # EXISTING: Vertex AI
│   │   ├── agent_service.py               # EXISTING: Agent management
│   │   └── gcp_auth_service.py            # EXISTING: Workload Identity
│   └── observability/
│       └── cloud_logging.py               # NEW: Structured logging
└── requirements.txt                        # Add google-cloud-logging

infrastructure/
├── terraform/
│   ├── gcs_buckets.tf                     # NEW: Onboarding bucket
│   ├── iam.tf                             # UPDATED: New service account
│   └── workload_identity.tf               # NEW: GitHub Actions WIF
└── monitoring/
    ├── dashboard.json                     # NEW: Monitoring dashboard
    └── alerts.tf                          # NEW: Alerting policies
```

---

## Environment Variables

### anzx-marketing (.env.production)
```bash
# Identity Platform
NEXT_PUBLIC_IDENTITY_PLATFORM_API_KEY=...
NEXT_PUBLIC_IDENTITY_PLATFORM_AUTH_DOMAIN=extreme-gecko-466211-t1.firebaseapp.com
NEXT_PUBLIC_IDENTITY_PLATFORM_PROJECT_ID=extreme-gecko-466211-t1

# Backend API
NEXT_PUBLIC_API_URL=https://core-api-<hash>-ts.a.run.app
NEXT_PUBLIC_API_REGION=australia-southeast1

# Feature Flags
NEXT_PUBLIC_ENABLE_AGENT_PROVISIONING=true
```

### core-api (Cloud Run environment)
```bash
# Already configured in existing deployment
GOOGLE_CLOUD_PROJECT=extreme-gecko-466211-t1
VERTEX_AI_LOCATION=australia-southeast1
RUNTIME_ENVIRONMENT=cloudrun

# New for Phase 2
GCS_ONBOARDING_BUCKET=anzx-user-onboarding
IDENTITY_PLATFORM_PROJECT_ID=extreme-gecko-466211-t1
ADMIN_NOTIFICATION_EMAIL=inderanz@gmail.com
```

---

## Success Criteria

- [ ] Customer can sign up with Google OAuth in < 5 seconds
- [ ] Agent provisioning completes in < 30 seconds
- [ ] All customer data stored in private GCS bucket with no public access
- [ ] Provisioning success rate > 95%
- [ ] API response time < 500ms (p95)
- [ ] Zero long-lived service account keys in code or CI/CD
- [ ] Complete audit trail in Cloud Logging
- [ ] Monitoring dashboard shows real-time metrics
- [ ] Integration tests pass in staging environment

---

## Deployment Sequence

1. **Infrastructure Setup** (Tasks 1-3, 22)
   - Enable Identity Platform
   - Create GCS bucket with security settings
   - Configure IAM roles and Workload Identity

2. **Backend Implementation** (Tasks 4-7, 18, 21)
   - Add public API endpoints to core-api
   - Implement GCS storage service
   - Add Cloud Logging integration
   - Deploy updated core-api to Cloud Run

3. **Frontend Implementation** (Tasks 8-12)
   - Update agent templates
   - Create sign-up component
   - Add "Hire Me" buttons
   - Create provisioning modal
   - Update /get-started page

4. **Client Libraries** (Tasks 13-17)
   - Implement all client libraries
   - Connect to core-api endpoints

5. **Monitoring & CI/CD** (Tasks 19-20, 23-24)
   - Create monitoring dashboard
   - Set up alerting
   - Configure GitHub Actions with WIF
   - Deploy anzx-marketing to Cloud Run

6. **Testing & Documentation** (Tasks 25-28)
   - Write comprehensive tests
   - Create documentation
   - Perform security testing
   - Launch to production

---

## Timeline Estimate

- **Phase 2.1:** 1 week (Infrastructure Setup - Tasks 1-3)
- **Phase 2.2:** 1 week (Agent Templates & Core Services - Tasks 4-7)
- **Phase 2.3:** 2 weeks (Backend API Endpoints - Tasks 8-11)
- **Phase 2.4:** 2 weeks (Frontend Integration - Tasks 12-15)
- **Phase 2.5:** 1 week (Client Libraries - Tasks 16-20)
- **Phase 2.6:** 1 week (Monitoring & Observability - Tasks 21-22)
- **Phase 2.7:** 1 week (CI/CD & Deployment - Tasks 23-25)
- **Phase 2.8:** 1 week (Testing & Documentation - Tasks 26-29)

**Total:** 10 weeks (~2.5 months)

## Dependency Graph

```
Phase 2.1 (Infrastructure)
    ↓
Phase 2.2 (Templates & Services) ← MUST complete before Phase 2.3
    ↓
Phase 2.3 (Backend APIs) ← Depends on Phase 2.2
    ↓
Phase 2.4 (Frontend) ← Depends on Phase 2.3
    ↓
Phase 2.5 (Client Libraries) ← Depends on Phase 2.3
    ↓
Phase 2.6 (Monitoring) ← Can start after Phase 2.2
    ↓
Phase 2.7 (CI/CD & Deployment) ← Depends on Phases 2.4, 2.5
    ↓
Phase 2.8 (Testing) ← Depends on Phase 2.7
```

---

## Notes

- All backend services already deployed on Cloud Run in australia-southeast1
- Vertex AI integration already working in production
- Database (PostgreSQL + pgvector) already configured
- Workload Identity already set up for core-api
- This phase focuses on customer-facing flows and integration
- No changes needed to existing agent-orchestration or knowledge-service
- Leverage existing billing, auth, and agent management infrastructure

