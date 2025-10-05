# Requirements Document: Real Agent Provisioning System

## Introduction

This document defines the requirements for Phase 2 of the ANZX AI platform, which transforms the marketing website into a fully functional agent provisioning system. Customers will be able to sign up via Google Identity Platform, hire specific AI agents through a "Hire Me" flow, and have those agents provisioned in Google Agentspace and deployed to Vertex AI Agent Engine with proper security, monitoring, and billing integration.

## Requirements

### Requirement 1: Google Identity Platform Authentication

**User Story:** As a customer, I want to sign up and authenticate using my Google account, so that I can securely access the ANZX platform without creating another password.

#### Acceptance Criteria

1. WHEN a user visits `/get-started` THEN the system SHALL display a "Sign up with Google" button
2. WHEN a user clicks "Sign up with Google" THEN the system SHALL initiate Google OAuth flow via Identity Platform
3. WHEN Google authentication succeeds THEN the system SHALL verify the ID token server-side
4. WHEN the ID token is verified THEN the system SHALL create a secure session for the user
5. IF the user is new THEN the system SHALL collect minimal profile information (name, email, company)
6. WHEN profile is collected THEN the system SHALL store only essential data with explicit consent
7. THEN the system SHALL NOT store any Google credentials or refresh tokens in application code

### Requirement 2: Secure Customer Data Storage in GCS

**User Story:** As a platform administrator, I want customer onboarding data stored securely in a private GCS bucket, so that we maintain data privacy and comply with security best practices.

#### Acceptance Criteria

1. WHEN the system stores customer data THEN it SHALL use a private GCS bucket named `anzx-user-onboarding`
2. WHEN the bucket is created THEN it SHALL have Uniform bucket-level access enabled
3. WHEN the bucket is configured THEN it SHALL have NO public ACLs or public access
4. WHEN objects are written THEN they SHALL be owned by a dedicated service account
5. IF CMEK encryption is available THEN the system SHALL provide configuration stubs for customer-managed encryption keys
6. WHEN a customer completes onboarding THEN the system SHALL write a JSON record to `users/{userId}/onboarding/{agentTemplateId}.json`
7. WHEN writing data THEN the record SHALL include: userId, email, agentTemplateId, businessProfile, dataSources, requestedCapabilities, timestamp
8. WHEN the service account accesses the bucket THEN it SHALL have ONLY `roles/storage.objectCreator` and `roles/storage.objectViewer` permissions

### Requirement 3: Agent-Specific "Hire Me" Flow

**User Story:** As a customer, I want to click "Hire Me" on a specific agent card and complete a tailored sign-up form, so that I can quickly provision the exact agent I need for my business.

#### Acceptance Criteria

1. WHEN a user views an agent card THEN the system SHALL display a prominent "Hire Me" button
2. WHEN a user clicks "Hire Me" THEN the system SHALL open a modal or redirect to `/get-started?agent={agentId}`
3. WHEN the form loads THEN it SHALL be pre-selected to the chosen agent template
4. WHEN the form renders THEN it SHALL display fields specific to that agent template from `adk-templates.ts`
5. IF the agent is Emma (recruiting) THEN the form SHALL request: ATS integration details, hiring volume, job types
6. IF the agent is Olivia (customer service) THEN the form SHALL request: support channels, ticket volume, helpdesk software
7. IF the agent is Jack (sales) THEN the form SHALL request: CRM system, lead sources, sales process details
8. WHEN the user is not authenticated THEN the system SHALL require Google sign-in before showing the agent-specific form
9. WHEN the form is submitted THEN the system SHALL validate all required fields per the template schema

### Requirement 4: Agent Provisioning via Agentspace and Vertex AI

**User Story:** As a customer, I want my hired agent to be automatically provisioned and deployed, so that I can start using it immediately without manual setup.

#### Acceptance Criteria

1. WHEN a customer submits the hire form THEN the system SHALL write the onboarding record to GCS
2. WHEN the onboarding record is saved THEN the system SHALL call `agentspace-client.ts.createAgent()`
3. WHEN `createAgent()` is called THEN it SHALL create an agent instance in Google Agentspace with name, description, tools, and policy packs
4. WHEN the Agentspace agent is created THEN the system SHALL receive an `agentId`
5. WHEN the `agentId` is received THEN the system SHALL call `vertex-ai-client.ts.deployAgent(agentId, region)`
6. WHEN `deployAgent()` is called THEN it SHALL deploy the agent to Vertex AI Agent Engine
7. WHEN deployment succeeds THEN the system SHALL receive a `deploymentId` and `endpoint` URL
8. WHEN deployment data is received THEN the system SHALL save an entry in `mcp-config.ts` binding `userId ↔ agentId ↔ deploymentId`
9. IF the customer requested multi-agent collaboration THEN the system SHALL call `a2a-client.ts.linkAgents()`
10. WHEN any provisioning step fails THEN the system SHALL implement exponential backoff retry logic per Google Cloud best practices

### Requirement 5: Conversation Context Management

**User Story:** As a customer, I want my agent to maintain conversation context across sessions, so that it provides consistent and contextually aware responses.

#### Acceptance Criteria

1. WHEN an agent is provisioned THEN the system SHALL create a context configuration in `mcp-config.ts`
2. WHEN the configuration is created THEN it SHALL include: deploymentId, endpoint, contextConfig, conversation-state strategy
3. WHEN the configuration is stored THEN it SHALL be keyed by `{userId, agentId}`
4. WHEN a conversation starts THEN the system SHALL load the context configuration
5. WHEN context is needed THEN the system SHALL provide grounding sources and context window settings
6. WHEN a conversation ends THEN the system SHALL persist the conversation state for future sessions

### Requirement 6: Cloud Logging and Monitoring

**User Story:** As a platform administrator, I want comprehensive logging and monitoring of agent provisioning and usage, so that I can troubleshoot issues and track system health.

#### Acceptance Criteria

1. WHEN the system performs any operation THEN it SHALL log to Google Cloud Logging using the Node.js client
2. WHEN logging THEN the system SHALL include request IDs and trace IDs for correlation
3. WHEN logging THEN the system SHALL use structured JSON format
4. WHEN logging user journey milestones THEN it SHALL include: sign-up, agent selection, provisioning start, provisioning complete, deployment ID
5. WHEN Vertex AI agents are deployed THEN the system SHALL export Vertex AI metrics to Cloud Monitoring
6. WHEN metrics are exported THEN the system SHALL create a dashboard JSON referencing: latency, request count, error rate
7. WHEN critical errors occur THEN the system SHALL provide configuration stubs for alerting policies

### Requirement 7: Usage-Based Billing Integration

**User Story:** As a platform administrator, I want to track agent usage and emit billing events, so that we can charge customers accurately based on their consumption.

#### Acceptance Criteria

1. WHEN an agent processes a request THEN the system SHALL emit a usage event
2. WHEN a usage event is emitted THEN it SHALL include: userId, agentId, timestamp, request type, token count
3. WHEN usage events are collected THEN the system SHALL expose a usage events emitter function hook
4. WHEN the billing system is ready THEN it SHALL consume these events to calculate charges
5. WHEN calculating usage THEN the system SHALL track: API calls, tokens processed, conversation minutes

### Requirement 8: Workload Identity Federation for CI/CD

**User Story:** As a platform engineer, I want CI/CD pipelines to authenticate to GCP without long-lived service account keys, so that we maintain security best practices and reduce credential exposure.

#### Acceptance Criteria

1. WHEN GitHub Actions runs THEN it SHALL use Workload Identity Federation to authenticate
2. WHEN authenticating THEN the system SHALL use `google-github-actions/auth` action
3. WHEN the workflow runs THEN it SHALL exchange GitHub OIDC token for short-lived GCP credentials
4. WHEN credentials are obtained THEN they SHALL be valid for the duration of the workflow only
5. WHEN configuring THEN the system SHALL document the Workload Identity pool and provider configuration
6. WHEN configuring THEN the system SHALL document required IAM bindings for the GitHub repository
7. THEN the system SHALL NOT use or store any long-lived service account keys in GitHub secrets

### Requirement 9: Template-Driven Agent Configuration

**User Story:** As a developer, I want agent templates to define their required fields and capabilities, so that the UI can dynamically render appropriate forms and the provisioning system knows what to configure.

#### Acceptance Criteria

1. WHEN defining an agent template THEN it SHALL include an `AgentTemplate` interface in `adk-templates.ts`
2. WHEN the template is defined THEN it SHALL specify: requiredFields, tools, safety settings, defaultPromptStyle
3. WHEN the template is defined THEN it SHALL specify data connector requirements
4. WHEN a "Hire Me" form loads THEN it SHALL read the template schema and render fields dynamically
5. WHEN provisioning an agent THEN the system SHALL use the template configuration to set up tools and policies
6. WHEN the template includes safety settings THEN the system SHALL apply them during Agentspace agent creation

### Requirement 10: Agent-to-Agent Communication

**User Story:** As a customer with multiple agents, I want my agents to collaborate and hand off tasks to each other, so that complex workflows can be automated across agent specialties.

#### Acceptance Criteria

1. WHEN a customer requests multi-agent collaboration THEN the system SHALL call `a2a-client.ts.linkAgents(primaryId, secondaryId, mode)`
2. WHEN agents are linked THEN the system SHALL register allowed cross-calls in the configuration
3. WHEN an agent needs to communicate THEN it SHALL use the A2A client to send messages
4. WHEN a message is sent THEN it SHALL include: sender agentId, recipient agentId, message content, context
5. WHEN a message is received THEN the recipient agent SHALL have access to the shared context

### Requirement 11: Security and IAM Best Practices

**User Story:** As a security engineer, I want all GCP resources to follow least-privilege IAM principles and security best practices, so that we minimize attack surface and comply with security standards.

#### Acceptance Criteria

1. WHEN creating service accounts THEN the system SHALL grant ONLY the minimum required roles
2. WHEN accessing GCS buckets THEN the system SHALL use service accounts with scoped permissions
3. WHEN deploying agents THEN the system SHALL use separate service accounts per customer or agent
4. WHEN configuring IAM THEN the system SHALL follow Google Cloud security best practices documentation
5. WHEN storing secrets THEN the system SHALL use Secret Manager, NOT environment variables or code
6. WHEN accessing APIs THEN the system SHALL use short-lived tokens, NOT long-lived keys

### Requirement 12: API Endpoints for Provisioning

**User Story:** As a frontend developer, I want well-defined API endpoints for authentication and provisioning, so that I can build the user interface with clear contracts.

#### Acceptance Criteria

1. WHEN implementing authentication THEN the system SHALL provide `POST /api/signup` endpoint
2. WHEN `/api/signup` is called THEN it SHALL verify the Identity Platform ID token
3. WHEN the token is verified THEN it SHALL write the onboarding JSON to GCS
4. WHEN implementing provisioning THEN the system SHALL provide `POST /api/agents/provision` endpoint
5. WHEN `/api/agents/provision` is called THEN it SHALL perform authorization checks
6. WHEN authorized THEN it SHALL orchestrate: create agent → deploy agent → persist config
7. WHEN implementing monitoring THEN the system SHALL provide `GET /api/agents/:id/status` endpoint
8. WHEN `/api/agents/:id/status` is called THEN it SHALL return health and metrics snapshot

### Requirement 13: Documentation and Runbook

**User Story:** As a platform engineer, I want comprehensive documentation of the provisioning system, so that I can deploy, maintain, and troubleshoot the platform effectively.

#### Acceptance Criteria

1. WHEN the system is implemented THEN the documentation SHALL include endpoint specifications
2. WHEN the system is implemented THEN the documentation SHALL include required IAM roles for each component
3. WHEN the system is implemented THEN the documentation SHALL include run commands for local development
4. WHEN the system is implemented THEN the documentation SHALL include deployment procedures
5. WHEN the system is implemented THEN the documentation SHALL include troubleshooting guides
6. WHEN the system is implemented THEN the documentation SHALL reference official Google Cloud documentation for each integration

