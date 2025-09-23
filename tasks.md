# ANZX.ai Platform - Implementation Roadmap

This document outlines the tasks that will be executed to complete the core functionality of the ANZX.ai platform. Each task will be completed and verified before proceeding to the next.

---

### Task 1: Implement `knowledge-service` Business Logic

-   **Status:** Completed
-   **Objective:** Build the core functionality for document processing, embedding, and search within the existing `knowledge-service`.
-   **Key Actions:**
    1.  Modify `services/knowledge-service/main.py` to add API endpoints.
    2.  Create a `POST /documents` endpoint for file uploads, saving files to Google Cloud Storage.
    3.  Implement a processing pipeline (text extraction, chunking, embedding via Vertex AI).
    4.  Store embeddings in the Cloud SQL (pgvector) database.
    5.  Create a `POST /search` endpoint to perform semantic search and return relevant document chunks.
-   **Verification:** Write a basic unit test to validate the search logic.

---

### Task 2: Implement `agent-orchestration` Service Logic

-   **Status:** Completed
-   **Objective:** Create the logic for routing queries and managing agent workflows.
-   **Key Actions:**
    1.  Modify `services/agent-orchestration/main.py`.
    2.  Create a `POST /orchestrate` endpoint that receives user queries.
    3.  Integrate with the `knowledge-service` to fetch relevant context for the query.
    4.  Use LangGraph to define a simple agent workflow that combines the user query and the fetched context into a prompt for a language model.
    5.  Return the final AI-generated response.
-   **Verification:** Write a basic unit test to validate the orchestration flow.

---

### Task 3: Update Infrastructure to Deploy All Services

-   **Status:** Completed
-   **Objective:** Add the `agent-orchestration` and `chat-widget` to the main Terraform configuration to make them deployable.
-   **Key Actions:**
    1.  Modify `infrastructure/terraform/main.tf`.
    2.  Add a `google_cloud_run_service` resource for the `agent-orchestration` service, mirroring the existing service configurations.
    3.  Add a `google_cloud_run_service` resource for the `chat-widget` service.
-   **Verification:** The syntax will be validated locally. Final verification will occur when the user runs the `scripts/deploy-infrastructure-fixed.sh` script.

---

### Task 4: Build the "Support Assistant"

-   **Status:** Completed
-   **Objective:** Implement a specific, functional AI assistant as a proof-of-concept.
-   **Key Actions:**
    1.  Within the `agent-orchestration` service, create a dedicated workflow for the "Support Assistant".
    2.  This workflow will use a specific system prompt tailored for customer support.
    3.  It will heavily rely on the `knowledge-service` to answer questions based on the provided documents.
-   **Verification:** The E2E test from Task 5 will validate this functionality.

---

### Task 5: Write an End-to-End Test

-   **Status:** Completed
-   **Objective:** Create a new test to verify the entire system works from end to end.
-   **Key Actions:**
    1.  Create a new Playwright test file in the `/tests` directory.
    2.  The test will make an API call to the `core-api` that simulates a user asking a question.
    3.  It will assert that a valid, non-empty AI response is received, confirming that all services (`core-api`, `agent-orchestration`, `knowledge-service`) worked together correctly.
-   **Verification:** The successful run of this test will mark the completion of the implementation.

---

### Task 6: Resolve Terraform State Lock

-   **Status:** Completed
-   **Objective:** Remove the stale lock on the Terraform state file to allow infrastructure changes to be applied.
-   **Key Actions:**
    1.  Run `terraform force-unlock` with the specific lock ID from the error log.
    2.  Re-run the Google Cloud Build deployment job.
-   **Verification:** The successful application of the subsequent deployment will verify the fix.

---

### Task 7: Fix Missing Terraform Variable

-   **Status:** Completed
-   **Objective:** Add the missing `firebase_token` variable to the Cloud Build configuration to allow Terraform to run.
-   **Key Actions:**
    1.  Modify `cloudbuild-infrastructure-fixed.yaml` to include a placeholder for `firebase_token`.
    2.  Re-run the Google Cloud Build deployment job.
-   **Verification:** A successful deployment will verify the fix.
