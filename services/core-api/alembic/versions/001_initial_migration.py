"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=10), nullable=True, default='AU'),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='Australia/Sydney'),
        sa.Column('subscription_plan', sa.String(length=50), nullable=True, default='freemium'),
        sa.Column('subscription_status', sa.String(length=50), nullable=True, default='active'),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('monthly_message_limit', sa.Integer(), nullable=True, default=1000),
        sa.Column('monthly_message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('monthly_token_limit', sa.Integer(), nullable=True, default=100000),
        sa.Column('monthly_token_count', sa.Integer(), nullable=True, default=0),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('branding', sa.JSON(), nullable=True),
        sa.Column('email_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_organizations_stripe_customer', 'organizations', ['stripe_customer_id'])
    op.create_index('idx_organizations_subscription_status', 'organizations', ['subscription_status'])
    op.create_index('idx_organizations_region', 'organizations', ['region'])

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('firebase_uid', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True, default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=True, default=0),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('notification_settings', sa.JSON(), nullable=True),
        sa.Column('privacy_consent', sa.Boolean(), nullable=True, default=False),
        sa.Column('privacy_consent_date', sa.DateTime(), nullable=True),
        sa.Column('marketing_consent', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('firebase_uid'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_organization_role', 'users', ['organization_id', 'role'])
    op.create_index('idx_users_active', 'users', ['is_active'])

    # Create assistants table
    op.create_table('assistants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('model_config', sa.JSON(), nullable=True),
        sa.Column('tools_config', sa.JSON(), nullable=True),
        sa.Column('knowledge_sources', postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('deployment_status', sa.String(length=50), nullable=True, default='draft'),
        sa.Column('version', sa.String(length=50), nullable=True, default='1.0.0'),
        sa.Column('total_conversations', sa.Integer(), nullable=True, default=0),
        sa.Column('total_messages', sa.Integer(), nullable=True, default=0),
        sa.Column('average_response_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('satisfaction_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_assistants_organization_type', 'assistants', ['organization_id', 'type'])
    op.create_index('idx_assistants_active', 'assistants', ['is_active'])
    op.create_index('idx_assistants_deployment_status', 'assistants', ['deployment_status'])

    # Create knowledge_sources table
    op.create_table('knowledge_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('processing_progress', sa.Float(), nullable=True, default=0.0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=True, default=0),
        sa.Column('chunking_config', sa.JSON(), nullable=True),
        sa.Column('embedding_model', sa.String(length=100), nullable=True, default='text-embedding-004'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_sources_organization', 'knowledge_sources', ['organization_id'])
    op.create_index('idx_knowledge_sources_status', 'knowledge_sources', ['status'])
    op.create_index('idx_knowledge_sources_type', 'knowledge_sources', ['type'])

    # Create documents table
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True, default=0),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_documents_knowledge_source', 'documents', ['knowledge_source_id'])
    op.create_index('idx_documents_chunk_index', 'documents', ['knowledge_source_id', 'chunk_index'])
    op.create_index('idx_documents_content_hash', 'documents', ['content_hash'])

    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=True, default='widget'),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='active'),
        sa.Column('resolution_status', sa.String(length=50), nullable=True),
        sa.Column('satisfaction_rating', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('total_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('total_cost', sa.Numeric(precision=10, scale=6), nullable=True, default=0),
        sa.Column('average_response_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assistant_id'], ['assistants.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_organization', 'conversations', ['organization_id'])
    op.create_index('idx_conversations_user', 'conversations', ['user_id'])
    op.create_index('idx_conversations_assistant', 'conversations', ['assistant_id'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])
    op.create_index('idx_conversations_channel', 'conversations', ['channel'])
    op.create_index('idx_conversations_created_at', 'conversations', ['created_at'])

    # Create messages table
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('tokens_input', sa.Integer(), nullable=True, default=0),
        sa.Column('tokens_output', sa.Integer(), nullable=True, default=0),
        sa.Column('cost', sa.Numeric(precision=10, scale=6), nullable=True, default=0),
        sa.Column('latency_ms', sa.Integer(), nullable=True, default=0),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('tool_results', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('feedback_rating', sa.Integer(), nullable=True),
        sa.Column('feedback_comment', sa.Text(), nullable=True),
        sa.Column('citations', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation', 'messages', ['conversation_id'])
    op.create_index('idx_messages_role', 'messages', ['role'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index('idx_messages_model', 'messages', ['model'])

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, default='active'),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('usage_counters', sa.JSON(), nullable=True),
        sa.Column('usage_limits', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('organization_id')
    )
    op.create_index('idx_subscriptions_stripe_customer', 'subscriptions', ['stripe_customer_id'])
    op.create_index('idx_subscriptions_stripe_subscription', 'subscriptions', ['stripe_subscription_id'])
    op.create_index('idx_subscriptions_status', 'subscriptions', ['status'])

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True, default='low'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_event_type', 'audit_logs', ['event_type'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_organization', 'audit_logs', ['organization_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_logs_risk_level', 'audit_logs', ['risk_level'])
    op.create_index('idx_audit_logs_outcome', 'audit_logs', ['outcome'])

    # Create vector index for documents (after table creation)
    op.execute('CREATE INDEX idx_documents_embedding_cosine ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

    # Insert initial development data
    op.execute("""
        INSERT INTO organizations (id, name, subscription_plan, subscription_status, created_at, updated_at)
        VALUES (
            uuid_generate_v4(),
            'ANZX Development',
            'enterprise',
            'active',
            NOW(),
            NOW()
        )
    """)

    # Log initialization
    op.execute("""
        INSERT INTO audit_logs (event_type, action, outcome, details, created_at)
        VALUES ('database', 'INIT', 'success', '{"message": "Database initialized successfully"}', NOW())
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('subscriptions')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('documents')
    op.drop_table('knowledge_sources')
    op.drop_table('assistants')
    op.drop_table('users')
    op.drop_table('organizations')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')