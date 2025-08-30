# ANZx.ai Database Documentation

## Overview

The ANZx.ai platform uses PostgreSQL with pgvector extension for storing application data and vector embeddings. This document covers the database schema, setup, and management.

## Database Schema

### Core Tables

#### Organizations
- **Purpose**: Multi-tenant organization management
- **Key Features**: Subscription tracking, usage limits, regional compliance
- **Relationships**: One-to-many with users, assistants, knowledge sources

#### Users
- **Purpose**: User authentication and profile management
- **Key Features**: Firebase integration, role-based access, privacy consent tracking
- **Relationships**: Many-to-one with organizations, one-to-many with conversations

#### Assistants
- **Purpose**: AI assistant configuration and performance tracking
- **Key Features**: Multi-type support (support, admin, content, insights), deployment status
- **Relationships**: Many-to-one with organizations, one-to-many with conversations

#### Knowledge Sources & Documents
- **Purpose**: RAG system for document processing and vector search
- **Key Features**: pgvector embeddings, hybrid search, chunking configuration
- **Relationships**: Knowledge sources contain multiple document chunks

#### Conversations & Messages
- **Purpose**: Chat history and performance tracking
- **Key Features**: Multi-channel support, cost tracking, satisfaction ratings
- **Relationships**: Conversations contain multiple messages

#### Subscriptions
- **Purpose**: Billing and usage tracking
- **Key Features**: Stripe integration, usage metering, plan management
- **Relationships**: One-to-one with organizations

#### Audit Logs
- **Purpose**: Compliance and security tracking
- **Key Features**: Risk assessment, detailed event logging
- **Relationships**: References users and organizations

## Database Setup

### Prerequisites

1. **PostgreSQL 14+** with the following extensions:
   - `vector` (pgvector for embeddings)
   - `pg_trgm` (trigram matching for text search)
   - `btree_gin` (GIN indexes)
   - `uuid-ossp` (UUID generation)

2. **Python Dependencies**:
   ```bash
   pip install sqlalchemy alembic psycopg2-binary pgvector
   ```

### Local Development Setup

1. **Start PostgreSQL with Docker**:
   ```bash
   docker run -d \
     --name anzx-postgres \
     -e POSTGRES_DB=anzx_platform \
     -e POSTGRES_USER=anzx_user \
     -e POSTGRES_PASSWORD=anzx_password \
     -p 5432:5432 \
     pgvector/pgvector:pg16
   ```

2. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://anzx_user:anzx_password@localhost:5432/anzx_platform"
   export JWT_SECRET="your-secret-key"
   ```

3. **Run Migrations**:
   ```bash
   python manage_db.py migrate
   ```

4. **Seed Sample Data** (optional):
   ```bash
   python manage_db.py seed
   ```

### Production Setup

1. **Cloud SQL Configuration**:
   - Enable pgvector extension
   - Configure connection pooling
   - Set up read replicas for scaling

2. **Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db
   READ_REPLICA_URL=postgresql://user:pass@read-host:5432/db
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=40
   ```

## Database Management

### Migration Commands

```bash
# Run all pending migrations
python manage_db.py migrate

# Create new migration
python manage_db.py create-migration -m "Add new feature"

# Check database health
python manage_db.py health

# Initialize fresh database
python manage_db.py init

# Reset database (DANGER!)
python manage_db.py reset

# Seed sample data
python manage_db.py seed
```

### Alembic Commands

```bash
# Generate migration automatically
alembic revision --autogenerate -m "Description"

# Upgrade to latest
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Vector Search

### pgvector Configuration

The platform uses pgvector for semantic search with 768-dimensional embeddings from Vertex AI's text-embedding-004 model.

#### Index Configuration
```sql
-- Create vector index for cosine similarity
CREATE INDEX idx_documents_embedding_cosine 
ON documents USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

#### Search Examples

**Vector Similarity Search**:
```python
from app.utils.database import VectorSearchUtils

results = VectorSearchUtils.similarity_search(
    db=db_session,
    query_embedding=query_vector,
    organization_id=org_id,
    limit=10,
    similarity_threshold=0.7
)
```

**Hybrid Search** (Vector + Text):
```python
results = VectorSearchUtils.hybrid_search(
    db=db_session,
    query_text="customer support",
    query_embedding=query_vector,
    organization_id=org_id,
    vector_weight=0.7,
    text_weight=0.3
)
```

## Performance Optimization

### Connection Pooling

```python
# Configuration in database.py
POOL_SIZE = 10          # Base connections
MAX_OVERFLOW = 20       # Additional connections
POOL_TIMEOUT = 30       # Connection timeout
POOL_RECYCLE = 3600     # Connection lifetime
```

### Indexing Strategy

#### Primary Indexes
- UUID primary keys on all tables
- Foreign key indexes for relationships
- Composite indexes for common queries

#### Search Indexes
- Vector similarity (ivfflat)
- Text search (GIN with pg_trgm)
- Timestamp indexes for time-based queries

#### Performance Indexes
```sql
-- Conversation queries
CREATE INDEX idx_conversations_org_status_created 
ON conversations(organization_id, status, created_at);

-- Message queries  
CREATE INDEX idx_messages_conversation_created
ON messages(conversation_id, created_at);

-- User lookup
CREATE INDEX idx_users_email_active
ON users(email, is_active);
```

### Query Optimization

1. **Use Read Replicas**: Configure `READ_REPLICA_URL` for read-heavy operations
2. **Connection Pooling**: Tune pool sizes based on load
3. **Query Analysis**: Use `EXPLAIN ANALYZE` for slow queries
4. **Index Maintenance**: Regular `ANALYZE` and `REINDEX`

## Monitoring and Maintenance

### Health Checks

```python
# Database health endpoint
GET /health

# Response includes:
{
  "checks": {
    "database": {
      "status": "healthy",
      "extensions": ["vector", "pg_trgm", "btree_gin"],
      "pool_size": 10,
      "checked_out": 2,
      "overflow": 0
    }
  }
}
```

### Performance Monitoring

```python
from app.utils.database import DatabaseUtils

# Get table statistics
stats = DatabaseUtils.get_table_stats(db)

# Get performance metrics
metrics = DatabaseUtils.get_performance_metrics(db)

# Optimize vector indexes
DatabaseUtils.optimize_vector_index(db)
```

### Maintenance Tasks

1. **Regular Cleanup**:
   ```python
   # Clean up old audit logs and conversations
   DatabaseUtils.cleanup_old_data(db, days=90)
   ```

2. **Index Optimization**:
   ```sql
   -- Analyze tables for query planner
   ANALYZE;
   
   -- Reindex vector indexes
   REINDEX INDEX idx_documents_embedding_cosine;
   ```

3. **Backup Strategy**:
   - Daily automated backups
   - Point-in-time recovery
   - Cross-region replication

## Security Considerations

### Data Encryption
- **At Rest**: AES-256 encryption via Cloud SQL
- **In Transit**: TLS 1.2+ for all connections
- **Application Level**: Sensitive fields encrypted before storage

### Access Control
- **Role-based Access**: User roles enforced at application level
- **Organization Isolation**: Multi-tenant data separation
- **Audit Logging**: All data access logged for compliance

### Compliance Features
- **Australian Privacy Principles**: Consent tracking, data portability
- **Data Breach Notification**: Automated breach detection and reporting
- **Retention Policies**: Automated cleanup of old data

## Troubleshooting

### Common Issues

1. **Connection Pool Exhaustion**:
   ```
   Error: QueuePool limit of size 10 overflow 20 reached
   Solution: Increase POOL_SIZE and MAX_OVERFLOW
   ```

2. **Slow Vector Queries**:
   ```
   Solution: Optimize ivfflat index with REINDEX
   Check lists parameter (default 100)
   ```

3. **Migration Failures**:
   ```
   Solution: Check database permissions
   Ensure extensions are installed
   Review migration logs
   ```

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=true
export LOG_SLOW_QUERIES=true
export SLOW_QUERY_THRESHOLD=1.0
```

### Performance Tuning

PostgreSQL configuration for production:
```sql
-- Memory settings
shared_buffers = '256MB'
effective_cache_size = '1GB'
work_mem = '4MB'

-- Vector-specific settings
max_connections = 100
shared_preload_libraries = 'vector'
```

## Migration Guide

### From Development to Production

1. **Export Schema**:
   ```bash
   pg_dump --schema-only anzx_platform > schema.sql
   ```

2. **Import to Production**:
   ```bash
   psql production_db < schema.sql
   ```

3. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

### Version Upgrades

1. **Backup Database**
2. **Test Migration on Staging**
3. **Run Migration with Downtime Window**
4. **Verify Data Integrity**
5. **Monitor Performance**

## API Integration

The database models integrate seamlessly with the FastAPI application:

```python
# Dependency injection
from app.models.database import get_db, get_read_db

@app.get("/organizations/{org_id}")
async def get_organization(
    org_id: str,
    db: Session = Depends(get_read_db)  # Use read replica
):
    return db.query(Organization).filter(Organization.id == org_id).first()
```

For more information, see the API documentation at `/docs` when running the application.