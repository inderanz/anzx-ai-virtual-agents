# ANZx.ai Platform Infrastructure

* Core API (`core-api`):
       * Purpose: Acts as the central gateway. It handles user authentication, organization management, billing
         (via Stripe), and routing requests to other backend services.
       * AI/GCP Services:
           * Vertex AI (`google-cloud-aiplatform`): Used for general AI capabilities.
           * Vertex AI Search (`google-cloud-discoveryengine`): Likely used for high-level, managed search over
             indexed data.
           * Postgres w/ `pgvector`: Directly interacts with the vector database for tasks that don't require
             the full knowledge-service.
           * Cloud Storage: Manages file uploads/downloads.

   * Knowledge Service (`knowledge-service`):
       * Purpose: This is the heart of the RAG (Retrieval-Augmented Generation) pipeline. Its job is to ingest
         unstructured data from various sources, process it, and convert it into searchable vector embeddings.
       * AI/GCP Services:
           * Document AI (`google-cloud-documentai`): To parse and extract text and structure from complex
             documents like PDFs and images.
           * Vertex AI (`google-cloud-aiplatform`): Used to access embedding models (like text-embedding-004)
             and other AI functionalities.
           * Sentence-Transformers: A key open-source library used to generate the vector embeddings from text
             chunks.
           * Postgres w/ `pgvector`: This is where it stores the final vector embeddings for similarity search.
       * Other Capabilities: Includes libraries for web scraping (scrapy, selenium) and OCR (pytesseract),
         indicating it can ingest knowledge from websites and scanned documents.

   * Agent Orchestration (`agent-orchestration`):
       * Purpose: This service acts as the "brain." It receives a prompt (forwarded from the Core API) and uses
         an agentic framework to reason, access tools, and generate a final answer.
       * AI/GCP Services:
           * Vertex AI (`google-cloud-aiplatform`): Connects to and runs the generative models (e.g., Gemini).
           * LangGraph & LangChain: These are the core frameworks used to build the agent. LangGraph allows for
             creating complex, stateful, multi-step flows (e.g., "search knowledge base," "ask clarifying
             question," "generate final report").
       * Multi-LLM Support: It notably includes libraries for OpenAI and Anthropic, meaning agents could be
         configured to use models like GPT-4 or Claude in addition to Google's Gemini models.

         
Service Configurations & Connections

   1. Chat Widget (`chat-widget`):
       * Role: The user-facing interface. It's a vanilla JavaScript application that can be embedded on any
         website.
       * Connection: It initiates a WebSocket connection to the Core API (/api/chat-widget/ws/{widget_id}) for
         real-time communication. If WebSockets fail, it falls back to standard HTTP polling to the same API
         (/api/chat-widget/public/chat). All communication is with the Core API.

   2. Core API (`core-api`):
       * Role: The central nervous system. It manages authentication, user data, billing, and acts as a secure
         gateway to the other backend services. It is the only service the user's browser directly communicates
         with.
       * Connections:
           * Receives requests from: The Chat Widget.
           * Cloud SQL (Postgres): Connects to the database to manage user, organization, and assistant data.
           * Redis: Used for caching sessions and other ephemeral data.
           * Agent Orchestration: When a chat message requires an AI-powered response, the Core API forwards
             the request to the appropriate endpoint on the Agent Orchestration service (e.g.,
             /orchestrate/support).

   3. Knowledge Service (`knowledge-service`):
       * Role: The RAG (Retrieval-Augmented Generation) engine. It does not receive requests directly from the
         user or Core API during a chat. Its primary role is asynchronous document processing.
       * Connections & AI Usage:
           * Receives requests from: An administrator or system process that uses its /documents endpoint to
             upload files.
           * Cloud Storage: Stores the original uploaded documents (PDFs, etc.) for archival.
           * `sentence-transformers`: Uses the all-MiniLM-L6-v2 model to convert chunks of text into
             384-dimension vector embeddings.
           * Cloud SQL (Postgres w/ `pgvector`): Stores the text chunks and their corresponding vector
             embeddings in the document_chunks table.
           * Provides data to: The Agent Orchestration service via its /search endpoint.

   4. Agent Orchestration (`agent-orchestration`):
       * Role: The "brain" that constructs AI responses. It executes a logical sequence of steps to answer a
         user's query.
       * Connections & AI Usage:
           * Receives requests from: The Core API.
           * Knowledge Service: It makes an HTTP POST request to the Knowledge Service's /search endpoint,
             sending the user's query. The Knowledge Service performs a vector similarity search and returns
             the most relevant text chunks as "context".
           * Vertex AI (`langchain_google_vertexai`): After retrieving context, it constructs a detailed prompt
             containing both the original question and the retrieved context. It then sends this prompt to a
             Google Gemini model (gemini-1.5-pro) via the Vertex AI API to generate a final, context-aware
             answer.
           * LangGraph: This framework defines the sequence of operations: retrieve_context ->
             generate_response -> END.



This directory contains the Infrastructure as Code (IaC) configuration for the ANZx.ai platform using Terraform and Google Cloud Platform.

## Architecture Overview

The platform is deployed on Google Cloud Platform with the following components:

- **Cloud Run** - Containerized microservices (Core API, Agent Orchestration, Knowledge Service)
- **Cloud SQL** - PostgreSQL with pgvector extension for embeddings
- **Memorystore Redis** - Caching and message queuing
- **Cloud Storage** - Document storage and static assets
- **Artifact Registry** - Container image registry
- **Cloud Build** - CI/CD pipelines
- **Cloud KMS** - Encryption key management
- **Secret Manager** - Secure secret storage
- **Cloud Monitoring** - Observability and alerting

## Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Terraform** >= 1.0 installed
3. **GCP Organization** with billing enabled
4. **GitHub repository** connected to Cloud Build

## Initial Setup

### 1. GCP Project Setup

Run the setup script to create GCP projects and prerequisites:

```bash
# Get your organization and billing account IDs
gcloud organizations list
gcloud billing accounts list

# Run setup script
./scripts/setup-gcp.sh [ORGANIZATION_ID] [BILLING_ACCOUNT_ID]
```

This script will:
- Create dev, staging, and prod GCP projects
- Enable required APIs
- Create Terraform state buckets
- Set up service accounts and permissions

### 2. Configure Authentication

```bash
# Set the service account key for Terraform
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/terraform-key.json

# Verify authentication
gcloud auth list
```

### 3. Update Configuration

Update the following files with your actual values:

1. **Project IDs** in `terraform/cloudbuild.tf`
2. **GitHub repository** details in Cloud Build triggers
3. **Domain names** in environment `.tfvars` files
4. **Slack webhook URLs** in monitoring configuration

## Deployment

### Development Environment

```bash
# Initialize Terraform
./scripts/deploy.sh dev init

# Plan infrastructure changes
./scripts/deploy.sh dev plan

# Apply changes
./scripts/deploy.sh dev apply
```

### Staging Environment

```bash
./scripts/deploy.sh staging plan
./scripts/deploy.sh staging apply
```

### Production Environment

```bash
./scripts/deploy.sh prod plan
./scripts/deploy.sh prod apply
```

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── apis.tf             # GCP API enablement
│   ├── networking.tf       # VPC and networking
│   ├── database.tf         # Cloud SQL configuration
│   ├── redis.tf            # Memorystore Redis
│   ├── storage.tf          # Cloud Storage buckets
│   ├── security.tf         # KMS, secrets, IAM
│   ├── cloud_run.tf        # Cloud Run services
│   ├── monitoring.tf       # Monitoring and alerting
│   ├── cloudbuild.tf       # CI/CD configuration
│   └── environments/       # Environment-specific configs
│       ├── dev.tfvars
│       ├── staging.tfvars
│       └── prod.tfvars
├── cloudbuild/             # Cloud Build pipeline configs
│   ├── core-api.yaml
│   ├── agent-orchestration.yaml
│   ├── knowledge-service.yaml
│   └── chat-widget.yaml
└── scripts/                # Deployment scripts
    ├── deploy.sh           # Main deployment script
    └── setup-gcp.sh        # Initial GCP setup
```

## Environment Configuration

### Development
- **Project**: `anzx-ai-dev`
- **Domain**: `dev.anzx.ai`
- **Scaling**: 0-5 instances (scale to zero)
- **Database**: Small instance, single zone
- **Redis**: Basic tier

### Staging
- **Project**: `anzx-ai-staging`
- **Domain**: `staging.anzx.ai`
- **Scaling**: 1-8 instances
- **Database**: Medium instance, single zone
- **Redis**: Standard tier

### Production
- **Project**: `anzx-ai-prod`
- **Domain**: `anzx.ai`
- **Scaling**: 2-20 instances (always warm)
- **Database**: Large instance, regional HA with read replica
- **Redis**: Standard HA tier

## Security Features

- **Encryption at rest** using Cloud KMS
- **Private networking** with VPC and private service access
- **Secret management** with Secret Manager
- **IAM roles** with least privilege access
- **Container scanning** in CI/CD pipelines
- **TLS 1.2+** for all external communications

## Monitoring and Alerting

The infrastructure includes comprehensive monitoring:

- **SLOs** for availability and latency
- **Alert policies** for error rates, latency, and resource usage
- **Custom dashboard** with key metrics
- **Notification channels** for email and Slack

## CI/CD Pipeline

Each service has automated CI/CD with:

1. **Build** - Docker image creation
2. **Test** - Unit and integration tests
3. **Security scan** - Container vulnerability scanning
4. **Deploy** - Automated deployment to Cloud Run
5. **Health check** - Post-deployment verification

## Disaster Recovery

- **Automated backups** with point-in-time recovery
- **Cross-region replication** for production
- **Infrastructure as Code** for rapid environment recreation
- **Monitoring and alerting** for proactive issue detection

## Cost Optimization

- **Auto-scaling** based on demand
- **Scale-to-zero** for development environments
- **Lifecycle policies** for storage buckets
- **Resource right-sizing** per environment

## Troubleshooting

### Common Issues

1. **Permission denied errors**
   ```bash
   # Verify service account permissions
   gcloud auth list
   gcloud projects get-iam-policy [PROJECT_ID]
   ```

2. **Terraform state issues**
   ```bash
   # List workspaces
   terraform workspace list
   
   # Switch workspace
   terraform workspace select [ENVIRONMENT]
   ```

3. **API not enabled errors**
   ```bash
   # Enable required APIs manually
   gcloud services enable [API_NAME] --project=[PROJECT_ID]
   ```

### Useful Commands

```bash
# View infrastructure outputs
terraform output

# Check service status
gcloud run services list --project=[PROJECT_ID]

# View logs
gcloud logging read "resource.type=cloud_run_revision" --project=[PROJECT_ID]

# Check database status
gcloud sql instances list --project=[PROJECT_ID]
```

## Support

For infrastructure issues:
1. Check the monitoring dashboard
2. Review Cloud Build logs
3. Examine Terraform state and outputs
4. Contact the platform team with specific error messages