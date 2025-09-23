# ANZX.ai Platform: Project State Analysis (Live)

This document provides a comprehensive analysis of the ANZX.ai Platform project, based on a review of the codebase, infrastructure-as-code, and live GCP deployment status as of September 21, 2025.

## 1. Feature Implementation Status

| Task ID | Feature Group | Status | Evidence & Analysis |
| :--- | :--- | :--- | :--- |
| **1.x** | **Project Foundation** | **Largely Implemented** | Monorepo, Dockerfiles, and Terraform configurations are in place for all services. |
| **2.x** | **Core API & Auth** | **Largely Implemented** | `services/core-api` is mature, handling auth, billing, and routing. Connects to DB and Redis. |
| **3.x** | **Google Agent Space** | **Partially Implemented** | The `agent-orchestration` service contains a working LangGraph implementation using a Gemini model (`gemini-1.5-pro`) via Vertex AI. It correctly calls the knowledge service for context. **Deployment is failing.** |
| **4.x** | **Knowledge & RAG** | **Partially Implemented** | The `knowledge-service` has a functional API for document ingestion and search. It uses `sentence-transformers` for embeddings and `pgvector` for storage. |
| **5.x** | **Multi-Channel Chat**| **Largely Implemented** | The `chat-widget` is a complete JS application with WebSocket and HTTP fallback logic connecting to the `core-api`. |
| **7.x** | **AI Assistants** | **Partially Implemented** | A "Support Assistant" agent is defined in `agent-orchestration`, demonstrating a concrete implementation of a specialized agent. |
| **8.x** | **Testing & QA** | **Partially Implemented** | `core-api` has a `pytest.ini` and a `tests/` directory. Playwright is configured, but E2E test coverage is likely minimal and needs to be expanded. |

## 2. Infrastructure and Deployment Analysis

### 2.1. Canonical Infrastructure

The single source of truth for infrastructure is `infrastructure/terraform/main.tf`. It correctly defines resources for all four microservices (`core-api`, `knowledge-service`, `agent-orchestration`, `chat-widget`), along with Cloud SQL, Redis, and Cloud Storage. There are no longer any gaps between the intended infrastructure in Terraform and the services that are supposed to be deployed.

### 2.2. Valid Deployment Process

The correct way to deploy is by executing `./scripts/deploy-infrastructure-fixed.sh`, which triggers a Cloud Build pipeline that runs Terraform.

## 3. Live System Status (as of 2025-09-21)

The following is a summary of the live configuration of services deployed in `australia-southeast1`, based on `gcloud` commands.

| Service Name | Status | Image Tag | Service Account | Key Environment Variables |
| :--- | :--- | :--- | :--- | :--- |
| `anzx-ai-platform-core-api` | **✔ Running** | `v1.0.4` | `anzx-ai-platform-run-sa@...` | `DATABASE_URL` |
| `anzx-ai-platform-knowledge-service` | **✔ Running** | `latest` | `anzx-ai-platform-run-sa@...` | `DATABASE_URL`, `GOOGLE_CLOUD_PROJECT` |
| `anzx-ai-platform-chat-widget` | **✔ Running** | `latest` | `...-compute@developer.gserviceaccount.com` | (none) |
| `anzx-ai-platform-agent-orch` | **✖ Failed** | `latest` | `anzx-ai-platform-run-sa@...` | `KNOWLEDGE_SERVICE_URL`, `VERTEX_AI_PROJECT` |

### 3.1. Analysis of Discrepancies

The primary discrepancy is between the *intended* state (a fully working system) and the *live* state:
1.  **`agent-orchestration` is CRITICAL**: The service is failing to deploy because its Docker image (`.../agent-orchestration:latest`) was not found in the Artifact Registry. This breaks the entire AI response generation flow.
2.  **Inconsistent Image Tagging**: The `core-api` uses a specific version (`v1.0.4`), while all other services use `latest`. This is poor practice and can lead to unpredictable deployments.
3.  **Insecure Service Account**: The `chat-widget` is using the default compute service account, which likely has overly broad permissions.

## 4. End-to-End Architecture Flow

This diagram illustrates the complete request and data flow for a typical user query.

```mermaid
graph TD
    subgraph "User's Browser"
        A[Chat Widget]
    end

    subgraph "GCP Cloud Run Services"
        B[Core API]
        C[Agent Orchestration]
        D[Knowledge Service]
    end

    subgraph "GCP Data & AI Services"
        E[Cloud SQL (Postgres w/ pgvector)]
        F[Redis]
        G[Vertex AI (Gemini 1.5 Pro)]
        H[Cloud Storage]
    end

    %% User Interaction Flow
    A -- "1. Send Message (WebSocket/HTTP)" --> B;

    %% Core API Logic
    B -- "2. Auth & Get User Data" --> E;
    B -- "3. Cache Session" --> F;
    B -- "4. Forward to Agent" --> C;

    %% Agent Orchestration Logic
    C -- "5. Retrieve Context" --> D;
    D -- "6. Vector Search in DB" --> E;
    D -- "7. Return Relevant Chunks" --> C;
    C -- "8. Generate Answer (Prompt + Context)" --> G;
    G -- "9. Return Generated Text" --> C;
    C -- "10. Return Final Answer" --> B;

    %% Final Response to User
    B -- "11. Send Response to Widget" --> A;

    %% Asynchronous Knowledge Ingestion Flow
    subgraph "Admin/System"
        J[Upload Document via API]
    end
    J -- "a. Upload PDF/TXT" --> D;
    D -- "b. Store Original in GCS" --> H;
    D -- "c. Create Embeddings & Store in DB" --> E;
```

## 5. Key Findings and Recommended Next Steps

### What is Working:

1.  **Infrastructure as Code**: All services are now correctly defined in Terraform, providing a single source of truth.
2.  **Core Services**: The `core-api`, `knowledge-service`, and `chat-widget` are deployed and running.
3.  **RAG Pipeline Logic**: The application code for the full retrieval-augmented generation flow is implemented and connects the services as intended.

### What to Work On Next:

1.  **Fix `agent-orchestration` Deployment (CRITICAL)**:
    *   **Immediate Action**: The Docker image for the `agent-orchestration` service must be successfully built and pushed to the Google Artifact Registry. The Cloud Build pipeline for this service (`infrastructure/cloudbuild/agent-orchestration.yaml`) should be used or debugged.
2.  **Improve Security & Governance**:
    *   **Action**: Update `infrastructure/terraform/main.tf` to assign the `anzx-ai-platform-run-sa` service account to the `chat-widget` service instead of the default compute account.
    *   **Action**: Update the Cloud Build pipelines for `chat-widget` and `knowledge-service` to build and push images with specific version tags (e.g., git commit hash) instead of `latest`.
3.  **Expand E2E Testing**:
    *   **Action**: Now that the full flow is defined, create E2E tests with Playwright that simulate a user interacting with the chat widget and triggering the full backend flow. This will be essential for validating the `agent-orchestration` fix.