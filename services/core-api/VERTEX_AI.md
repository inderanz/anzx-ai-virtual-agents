# ANZx.ai Vertex AI Agent Builder Integration

## Overview

The ANZx.ai platform integrates with Google Cloud's Vertex AI Agent Builder to provide sophisticated conversational AI capabilities. This integration enables the creation and management of AI agents that can handle customer support, administrative tasks, and other business functions with advanced natural language understanding and knowledge base integration.

## Architecture

### Core Components

#### 1. Vertex AI Configuration (`app/config/vertex_ai.py`)
- **Project Settings**: Google Cloud project and location configuration
- **Workload Identity**: Kubernetes service account mapping for secure authentication
- **Agent Templates**: Pre-configured templates for different agent types
- **Performance Settings**: Timeout, retry, and caching configurations

#### 2. GCP Authentication Service (`app/services/gcp_auth_service.py`)
- **Multi-Environment Support**: GKE, Cloud Run, and local development
- **Workload Identity Federation**: Secure authentication without service account keys
- **Credential Management**: Automatic credential refresh and validation
- **Permission Verification**: IAM permission checking and validation

#### 3. Vertex AI Service (`app/services/vertex_ai_service.py`)
- **Agent Creation**: Create and configure Vertex AI agents
- **Conversation Management**: Handle multi-turn conversations
- **Knowledge Integration**: Connect agents to knowledge bases
- **Performance Monitoring**: Track agent metrics and performance

#### 4. Agent Service (`app/services/agent_service.py`)
- **Database Integration**: Sync Vertex AI agents with local database
- **Usage Tracking**: Monitor token usage and costs
- **Conversation Persistence**: Store conversation history
- **Analytics**: Generate performance reports

## Authentication

### Workload Identity Federation

The platform uses Workload Identity Federation for secure authentication to Google Cloud services without storing service account keys.

#### GKE Configuration

```yaml
# Kubernetes Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: anzx-vertex-ai-sa
  namespace: default
  annotations:
    iam.gke.io/gcp-service-account: vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com

---
# Deployment using the service account
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anzx-core-api
spec:
  template:
    spec:
      serviceAccountName: anzx-vertex-ai-sa
      containers:
      - name: core-api
        image: gcr.io/anzx-ai-platform/core-api
        env:
        - name: RUNTIME_ENVIRONMENT
          value: "gke"
        - name: KUBERNETES_SERVICE_ACCOUNT
          value: "anzx-vertex-ai-sa"
```

#### Cloud Run Configuration

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: anzx-core-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/service-account: vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com
    spec:
      containers:
      - image: gcr.io/anzx-ai-platform/core-api
        env:
        - name: RUNTIME_ENVIRONMENT
          value: "cloudrun"
```

#### Required IAM Roles

The Google Service Account needs the following roles:

```bash
# Vertex AI roles
gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Discovery Engine roles
gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/discoveryengine.admin"

# Additional required roles
gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

## Agent Templates

### Support Agent Template

```python
{
    "display_name": "Customer Support Agent",
    "description": "AI assistant for customer support and help desk operations",
    "default_language_code": "en",
    "time_zone": "Australia/Sydney",
    "intents": [
        {
            "display_name": "Default Welcome Intent",
            "training_phrases": [
                "Hi", "Hello", "Good morning", "I need help"
            ],
            "messages": [
                {
                    "text": "Hello! I'm your AI support assistant. How can I help you today?"
                }
            ]
        }
    ],
    "entities": [
        {
            "display_name": "product",
            "entries": [
                {"value": "billing", "synonyms": ["payment", "invoice", "subscription"]},
                {"value": "technical", "synonyms": ["bug", "error", "issue"]}
            ]
        }
    ]
}
```

### Admin Agent Template

```python
{
    "display_name": "Administrative Assistant",
    "description": "AI assistant for administrative tasks and scheduling",
    "intents": [
        {
            "display_name": "Schedule Meeting",
            "training_phrases": [
                "Schedule a meeting", "Book a meeting", "Set up a call"
            ],
            "parameters": [
                {
                    "display_name": "date-time",
                    "entity_type": "@sys.date-time",
                    "mandatory": True
                }
            ]
        }
    ]
}
```

## API Usage

### Creating an Agent

```python
# Create agent through API
POST /api/v1/agents/
{
    "name": "Customer Support Bot",
    "description": "Handles customer inquiries and support tickets",
    "type": "support",
    "temperature": 0.7,
    "max_tokens": 1024,
    "enabled_tools": ["escalation", "knowledge_search"],
    "knowledge_sources": ["kb-faq-001", "kb-policies-002"]
}
```

### Starting a Conversation

```python
# Start conversation with agent
POST /api/v1/agents/{agent_id}/chat
{
    "message": "I need help with my billing",
    "channel": "widget",
    "context": {
        "user_tier": "premium",
        "previous_issues": []
    }
}

# Response
{
    "conversation_id": "conv-123",
    "message_id": "msg-456",
    "reply": "I'd be happy to help you with your billing. Could you please provide more details about the specific issue you're experiencing?",
    "citations": [
        {
            "title": "Billing FAQ",
            "uri": "https://docs.anzx.ai/billing-faq",
            "chunk_info": {"page": 1}
        }
    ],
    "usage": {
        "tokens_input": 15,
        "tokens_output": 32,
        "cost": 0.000047
    }
}
```

### Getting Agent Analytics

```python
# Get agent performance metrics
GET /api/v1/agents/{agent_id}/analytics?days=30

# Response
{
    "agent_id": "agent-123",
    "period_days": 30,
    "conversations": {
        "total": 1250,
        "messages": 3800,
        "avg_satisfaction": 4.2
    },
    "performance": {
        "avg_response_time_ms": 1200,
        "total_tokens": 125000,
        "total_cost": 12.50
    }
}
```

## Knowledge Base Integration

### Creating Data Stores

```python
# Create data store for knowledge base
async def create_data_store(organization_id: str, name: str) -> str:
    parent = f"projects/{project_id}/locations/{location}"
    
    data_store = discoveryengine.DataStore(
        display_name=name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_CHAT],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )
    
    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=f"datastore-{organization_id}-{name}"
    )
    
    operation = client.create_data_store(request=request)
    return request.data_store_id
```

### Document Ingestion

```python
# Add documents to data store
async def add_documents_to_datastore(
    data_store_id: str,
    documents: List[Dict[str, Any]]
) -> bool:
    for doc in documents:
        document = discoveryengine.Document(
            id=doc["id"],
            struct_data=doc["content"],
            parent_document_id=doc.get("parent_id")
        )
        
        request = discoveryengine.CreateDocumentRequest(
            parent=f"projects/{project_id}/locations/{location}/dataStores/{data_store_id}/branches/default_branch",
            document=document,
            document_id=doc["id"]
        )
        
        operation = client.create_document(request=request)
    
    return True
```

## Conversation Management

### Context Handling

```python
# Build conversation context
async def build_conversation_context(
    db: Session, 
    conversation_id: str
) -> Dict[str, Any]:
    # Get recent messages for context
    recent_messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(10).all()
    
    context = {
        "conversation_id": str(conversation_id),
        "message_count": len(recent_messages),
        "recent_messages": [
            {
                "role": msg.role,
                "content": msg.content[:200],  # Truncate for context
                "timestamp": msg.created_at.isoformat()
            }
            for msg in reversed(recent_messages)
        ]
    }
    
    return context
```

### Multi-turn Conversations

```python
# Continue existing conversation
response = await vertex_ai_service.start_conversation(
    agent_id="agent-support-123",
    user_message="Can you explain the refund policy?",
    conversation_id="conv-existing-456",
    context={
        "previous_topic": "billing_inquiry",
        "user_tier": "premium"
    }
)
```

## Performance Monitoring

### Usage Tracking

```python
# Track AI interaction usage
usage_stats = await usage_tracker.track_ai_interaction(
    db=db,
    organization_id=org_id,
    tokens_input=response["tokens_input"],
    tokens_output=response["tokens_output"],
    cost=response["cost"],
    model="gemini-1.0-pro"
)

# Check usage limits before processing
limit_check = await usage_tracker.check_usage_limits(
    db=db,
    organization_id=org_id,
    required_tokens=estimated_tokens
)

if not limit_check["can_proceed"]:
    raise HTTPException(
        status_code=429,
        detail="Usage limit exceeded"
    )
```

### Performance Metrics

```python
# Get comprehensive agent metrics
metrics = await vertex_ai_service.get_agent_metrics(
    agent_id="agent-123",
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)

# Metrics include:
# - Total conversations and messages
# - Average response time
# - Token usage and costs
# - Satisfaction scores
# - Error rates
```

## Error Handling

### Graceful Degradation

```python
try:
    # Try Vertex AI agent
    response = await vertex_ai_service.start_conversation(
        agent_id=agent_id,
        user_message=message
    )
except Exception as e:
    logger.error(f"Vertex AI error: {e}")
    
    # Fallback to simple response
    response = {
        "reply": "I'm experiencing technical difficulties. Please try again or contact support.",
        "conversation_id": conversation_id,
        "fallback": True
    }
```

### Retry Logic

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception)
)
async def call_vertex_ai_with_retry(request):
    return await vertex_ai_client.converse_conversation(request)
```

## Development Setup

### Environment Variables

```bash
# Google Cloud Configuration
export GOOGLE_CLOUD_PROJECT=anzx-ai-platform
export VERTEX_AI_LOCATION=us-central1
export AGENT_BUILDER_LOCATION=global

# Runtime Environment
export RUNTIME_ENVIRONMENT=local  # gke, cloudrun, local

# Authentication (local development only)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Vertex AI Settings
export VERTEX_AI_DEFAULT_MODEL=gemini-1.0-pro
export VERTEX_AI_EMBEDDING_MODEL=text-embedding-004
```

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install google-cloud-aiplatform google-cloud-discoveryengine
   ```

2. **Set up Authentication**:
   ```bash
   # Using gcloud CLI
   gcloud auth application-default login
   
   # Or using service account key
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```

3. **Test Connection**:
   ```bash
   # Test Vertex AI connection
   curl -X GET "http://localhost:8000/api/v1/agents/health/vertex-ai" \
        -H "Authorization: Bearer <token>"
   ```

### Testing

```bash
# Run Vertex AI tests
python -m pytest tests/test_vertex_ai.py -v

# Run specific test class
python -m pytest tests/test_vertex_ai.py::TestVertexAIService -v

# Run with coverage
python -m pytest tests/test_vertex_ai.py --cov=app.services.vertex_ai_service
```

## Production Deployment

### GKE Deployment

1. **Create Service Account**:
   ```bash
   # Create Google Service Account
   gcloud iam service-accounts create vertex-ai-service \
     --display-name="Vertex AI Service Account"
   
   # Grant required roles
   gcloud projects add-iam-policy-binding anzx-ai-platform \
     --member="serviceAccount:vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

2. **Configure Workload Identity**:
   ```bash
   # Enable Workload Identity on cluster
   gcloud container clusters update anzx-cluster \
     --workload-pool=anzx-ai-platform.svc.id.goog
   
   # Create Kubernetes Service Account
   kubectl create serviceaccount anzx-vertex-ai-sa
   
   # Bind accounts
   gcloud iam service-accounts add-iam-policy-binding \
     vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com \
     --role roles/iam.workloadIdentityUser \
     --member "serviceAccount:anzx-ai-platform.svc.id.goog[default/anzx-vertex-ai-sa]"
   
   # Annotate Kubernetes Service Account
   kubectl annotate serviceaccount anzx-vertex-ai-sa \
     iam.gke.io/gcp-service-account=vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com
   ```

### Cloud Run Deployment

```bash
# Deploy with service account
gcloud run deploy anzx-core-api \
  --image gcr.io/anzx-ai-platform/core-api \
  --service-account vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com \
  --set-env-vars RUNTIME_ENVIRONMENT=cloudrun \
  --region us-central1
```

## Monitoring and Observability

### Health Checks

```python
# Vertex AI health check endpoint
GET /api/v1/agents/health/vertex-ai

# Response
{
    "status": "healthy",
    "project_id": "anzx-ai-platform",
    "location": "us-central1",
    "config_validation": {
        "project_id_set": true,
        "location_set": true,
        "service_account_configured": true
    },
    "api_accessible": true,
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Logging

```python
# Structured logging for Vertex AI operations
logger.info(
    "Vertex AI conversation processed",
    extra={
        "agent_id": agent_id,
        "conversation_id": conversation_id,
        "tokens_used": tokens_input + tokens_output,
        "response_time_ms": response_time,
        "cost_usd": cost,
        "organization_id": organization_id
    }
)
```

### Metrics

Key metrics to monitor:
- **Response Time**: Average time for agent responses
- **Token Usage**: Input/output tokens per conversation
- **Cost Tracking**: Cost per interaction and monthly totals
- **Error Rates**: Failed requests and timeouts
- **Satisfaction Scores**: User feedback ratings

## Security Considerations

### Data Privacy

- **No PII in Logs**: Ensure no personally identifiable information is logged
- **Conversation Encryption**: All conversations encrypted at rest
- **Access Control**: Role-based access to agent management
- **Audit Logging**: Complete audit trail for compliance

### API Security

- **Authentication**: All requests require valid JWT tokens
- **Rate Limiting**: Prevent abuse with rate limiting
- **Input Validation**: Sanitize all user inputs
- **Output Filtering**: Filter sensitive information from responses

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy anzx-ai-platform \
     --flatten="bindings[].members" \
     --filter="bindings.members:vertex-ai-service@anzx-ai-platform.iam.gserviceaccount.com"
   ```

2. **Agent Creation Failures**:
   ```bash
   # Check Discovery Engine API is enabled
   gcloud services list --enabled --filter="name:discoveryengine.googleapis.com"
   ```

3. **Conversation Errors**:
   ```bash
   # Check agent status
   curl -X GET "http://localhost:8000/api/v1/agents/{agent_id}" \
        -H "Authorization: Bearer <token>"
   ```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Check authentication status
curl -X GET "http://localhost:8000/api/v1/agents/health/vertex-ai"
```

## Future Enhancements

### Planned Features

1. **Multi-language Support**: Support for multiple languages in agent responses
2. **Advanced Analytics**: More detailed performance and usage analytics
3. **Custom Models**: Integration with custom trained models
4. **Voice Integration**: Support for voice-based interactions
5. **Advanced Workflows**: Complex multi-step conversation flows

### Integration Roadmap

1. **Phase 1**: Basic agent creation and conversation handling ✅
2. **Phase 2**: Knowledge base integration and search
3. **Phase 3**: Advanced analytics and monitoring
4. **Phase 4**: Multi-modal interactions (text, voice, images)
5. **Phase 5**: Custom model training and deployment

The Vertex AI Agent Builder integration provides a robust foundation for sophisticated conversational AI capabilities while maintaining security, scalability, and compliance with Australian data protection requirements.