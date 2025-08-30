# ANZx.ai Platform Development Makefile

.PHONY: help build up down logs clean test lint format install-deps

# Default target
help:
	@echo "ANZx.ai Platform Development Commands"
	@echo "====================================="
	@echo "build          - Build all Docker containers"
	@echo "up             - Start all services"
	@echo "up-dev         - Start all services with dev tools (pgadmin, redis-commander)"
	@echo "down           - Stop all services"
	@echo "logs           - Show logs from all services"
	@echo "logs-api       - Show logs from core API service"
	@echo "logs-agent     - Show logs from agent orchestration service"
	@echo "logs-knowledge - Show logs from knowledge service"
	@echo "clean          - Clean up containers and volumes"
	@echo "test           - Run all tests"
	@echo "lint           - Run linting on all services"
	@echo "format         - Format code in all services"
	@echo "install-deps   - Install development dependencies"

# Docker operations
build:
	docker-compose build

up:
	docker-compose up -d

up-dev:
	docker-compose --profile dev up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f core-api

logs-agent:
	docker-compose logs -f agent-orchestration

logs-knowledge:
	docker-compose logs -f knowledge-service

clean:
	docker-compose down -v
	docker system prune -f

# Development operations
test:
	@echo "Running tests for all services..."
	cd services/core-api && python -m pytest tests/ -v
	cd services/agent-orchestration && python -m pytest tests/ -v
	cd services/knowledge-service && python -m pytest tests/ -v
	cd services/chat-widget && npm test

lint:
	@echo "Running linting for all services..."
	cd services/core-api && python -m flake8 .
	cd services/agent-orchestration && python -m flake8 .
	cd services/knowledge-service && python -m flake8 .
	cd services/chat-widget && npm run lint

format:
	@echo "Formatting code for all services..."
	cd services/core-api && python -m black .
	cd services/agent-orchestration && python -m black .
	cd services/knowledge-service && python -m black .
	cd services/chat-widget && npm run format

install-deps:
	@echo "Installing development dependencies..."
	cd services/core-api && pip install -r requirements.txt -r requirements-dev.txt
	cd services/agent-orchestration && pip install -r requirements.txt -r requirements-dev.txt
	cd services/knowledge-service && pip install -r requirements.txt -r requirements-dev.txt
	cd services/chat-widget && npm install

# Database operations
db-migrate:
	docker-compose exec core-api alembic upgrade head

db-reset:
	docker-compose exec postgres psql -U anzx_user -d anzx_platform -c "DROP SCHEMA IF EXISTS core CASCADE; DROP SCHEMA IF EXISTS knowledge CASCADE; DROP SCHEMA IF EXISTS conversations CASCADE;"
	docker-compose exec core-api alembic upgrade head

# Quick start
quick-start: build up
	@echo "ANZx.ai Platform is starting up..."
	@echo "Services will be available at:"
	@echo "  Core API: http://localhost:8000"
	@echo "  Agent Orchestration: http://localhost:8001"
	@echo "  Knowledge Service: http://localhost:8002"
	@echo "  Chat Widget: http://localhost:8003"
	@echo ""
	@echo "Development tools (run 'make up-dev'):"
	@echo "  PgAdmin: http://localhost:5050"
	@echo "  Redis Commander: http://localhost:8081"