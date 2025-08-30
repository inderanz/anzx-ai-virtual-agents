-- Initialize ANZx.ai Platform Database
-- Enable pgvector extension for embeddings

-- Create the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schemas for different services
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS knowledge;
CREATE SCHEMA IF NOT EXISTS conversations;

-- Set up initial database structure
-- This will be expanded by Alembic migrations

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA core TO anzx_user;
GRANT ALL PRIVILEGES ON SCHEMA knowledge TO anzx_user;
GRANT ALL PRIVILEGES ON SCHEMA conversations TO anzx_user;

-- Create initial indexes for performance
-- Additional indexes will be created by migrations