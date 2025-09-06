"""Add MCP tables

Revision ID: 007
Revises: 006
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create mcp_servers table
    op.create_table('mcp_servers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('pid', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('restart_count', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('capabilities', postgresql.JSON(), nullable=True),
        sa.Column('tools_count', sa.Integer(), nullable=True),
        sa.Column('resources_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_mcp_servers_org_name')
    )
    
    # Create mcp_tools table
    op.create_table('mcp_tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('server_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('input_schema', postgresql.JSON(), nullable=False),
        sa.Column('output_schema', postgresql.JSON(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=True),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('average_execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('security_policy', postgresql.JSON(), nullable=True),
        sa.Column('allowed_roles', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['server_id'], ['mcp_servers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('server_id', 'name', name='uq_mcp_tools_server_name')
    )
    
    # Create mcp_tool_executions table
    op.create_table('mcp_tool_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('input_parameters', postgresql.JSON(), nullable=False),
        sa.Column('output_result', postgresql.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(100), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_reason', sa.Text(), nullable=True),
        sa.Column('memory_usage_mb', sa.Integer(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('network_requests', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['tool_id'], ['mcp_tools.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_mcp_servers_organization', 'mcp_servers', ['organization_id'])
    op.create_index('idx_mcp_servers_name', 'mcp_servers', ['name'])
    op.create_index('idx_mcp_servers_status', 'mcp_servers', ['status'])
    op.create_index('idx_mcp_servers_active', 'mcp_servers', ['is_active'])
    
    op.create_index('idx_mcp_tools_server', 'mcp_tools', ['server_id'])
    op.create_index('idx_mcp_tools_organization', 'mcp_tools', ['organization_id'])
    op.create_index('idx_mcp_tools_name', 'mcp_tools', ['name'])
    op.create_index('idx_mcp_tools_category', 'mcp_tools', ['category'])
    op.create_index('idx_mcp_tools_enabled', 'mcp_tools', ['is_enabled'])
    
    op.create_index('idx_mcp_executions_tool', 'mcp_tool_executions', ['tool_id'])
    op.create_index('idx_mcp_executions_organization', 'mcp_tool_executions', ['organization_id'])
    op.create_index('idx_mcp_executions_user', 'mcp_tool_executions', ['user_id'])
    op.create_index('idx_mcp_executions_conversation', 'mcp_tool_executions', ['conversation_id'])
    op.create_index('idx_mcp_executions_status', 'mcp_tool_executions', ['status'])
    op.create_index('idx_mcp_executions_started_at', 'mcp_tool_executions', ['started_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_mcp_executions_started_at', table_name='mcp_tool_executions')
    op.drop_index('idx_mcp_executions_status', table_name='mcp_tool_executions')
    op.drop_index('idx_mcp_executions_conversation', table_name='mcp_tool_executions')
    op.drop_index('idx_mcp_executions_user', table_name='mcp_tool_executions')
    op.drop_index('idx_mcp_executions_organization', table_name='mcp_tool_executions')
    op.drop_index('idx_mcp_executions_tool', table_name='mcp_tool_executions')
    
    op.drop_index('idx_mcp_tools_enabled', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_category', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_name', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_organization', table_name='mcp_tools')
    op.drop_index('idx_mcp_tools_server', table_name='mcp_tools')
    
    op.drop_index('idx_mcp_servers_active', table_name='mcp_servers')
    op.drop_index('idx_mcp_servers_status', table_name='mcp_servers')
    op.drop_index('idx_mcp_servers_name', table_name='mcp_servers')
    op.drop_index('idx_mcp_servers_organization', table_name='mcp_servers')
    
    # Drop tables
    op.drop_table('mcp_tool_executions')
    op.drop_table('mcp_tools')
    op.drop_table('mcp_servers')