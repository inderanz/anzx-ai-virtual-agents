# ANZx.ai Platform

Advanced AI assistants, freeing up human entrepreneurs to focus on strategic work.

## Architecture

The ANZx.ai platform is built as a cloud-native microservices architecture with the following components:

### Services

- **Core API** (`services/core-api/`) - FastAPI service handling authentication, billing, and core business logic
- **Agent Orchestration** (`services/agent-orchestration/`) - AI agent management and conversation routing
- **Knowledge Service** (`services/knowledge-service/`) - Document processing, embeddings, and RAG system
- **Chat Widget** (`services/chat-widget/`) - Embeddable JavaScript widget for customer interactions

### Infrastructure

- **PostgreSQL with pgvector** - Primary database with vector embeddings support
- **Redis** - Caching and message queuing
- **Docker & Docker Compose** - Containerized development and deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Development Setup

1. **Clone and start the platform:**
   ```bash
   git clone <repository-url>
   cd anzx-ai-virtual-agents
   make quick-start
   ```

2. **Or manually with Docker Compose:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Access the services:**
   - Core API: http://localhost:8000
   - Agent Orchestration: http://localhost:8001
   - Knowledge Service: http://localhost:8002
   - Chat Widget: http://localhost:8003

4. **Development tools (optional):**
   ```bash
   make up-dev
   ```
   - PgAdmin: http://localhost:5050 (admin@anzx.ai / admin)
   - Redis Commander: http://localhost:8081

### Available Commands

```bash
make help           # Show all available commands
make build          # Build all containers
make up             # Start all services
make up-dev         # Start with development tools
make down           # Stop all services
make logs           # View logs from all services
make test           # Run all tests
make clean          # Clean up containers and volumes
```

## Development

### Project Structure

```
anzx-ai-virtual-agents/
├── services/
│   ├── core-api/           # FastAPI core service
│   ├── agent-orchestration/   # AI agent management
│   ├── knowledge-service/     # Document processing & RAG
│   └── chat-widget/          # Embeddable chat widget
├── scripts/                # Database and deployment scripts
├── .kiro/                  # Kiro IDE specifications
├── docker-compose.yml      # Local development environment
└── Makefile               # Development commands
```

### Adding New Features

1. Review the feature specifications in `.kiro/specs/anzx-ai-platform/`
2. Follow the implementation tasks outlined in `tasks.md`
3. Implement changes in the appropriate service
4. Add tests and update documentation
5. Test locally with `make test`

### Database Migrations

```bash
# Run migrations
make db-migrate

# Reset database (development only)
make db-reset
```

## Production Deployment

The platform is designed for deployment on Google Cloud Platform using:

- **Cloud Run** - Containerized service deployment
- **Cloud SQL** - Managed PostgreSQL with pgvector
- **Cloud Storage** - Document and asset storage
- **Cloud Build** - CI/CD pipeline
- **Cloud Monitoring** - Observability and alerting

See the infrastructure specifications in `.kiro/specs/anzx-ai-platform/design.md` for detailed deployment architecture.

## Contributing

1. Follow the development workflow outlined in the specifications
2. Ensure all tests pass before submitting changes
3. Follow the coding standards and linting rules
4. Update documentation for any new features

## License

MIT License - see LICENSE file for details.