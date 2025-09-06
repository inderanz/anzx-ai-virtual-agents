"""Add email integration tables

Revision ID: 006
Revises: 005
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add email_settings column to organizations table
    op.add_column('organizations', sa.Column('email_settings', postgresql.JSON(), nullable=True))
    
    # Create email_threads table
    op.create_table('email_threads',
        sa.Column('id', sa.String(32), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('customer_email', sa.String(255), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('message_references', sa.Text(), nullable=True),
        sa.Column('last_message_id', sa.String(255), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('last_response_at', sa.DateTime(), nullable=True),
        sa.Column('response_count', sa.Integer(), nullable=True),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),
        sa.Column('escalation_reason', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for email_threads
    op.create_index('idx_email_threads_organization', 'email_threads', ['organization_id'])
    op.create_index('idx_email_threads_conversation', 'email_threads', ['conversation_id'])
    op.create_index('idx_email_threads_customer_email', 'email_threads', ['customer_email'])
    op.create_index('idx_email_threads_status', 'email_threads', ['status'])
    op.create_index('idx_email_threads_priority', 'email_threads', ['priority'])
    op.create_index('idx_email_threads_created_at', 'email_threads', ['created_at'])
    op.create_index('idx_email_threads_last_message_at', 'email_threads', ['last_message_at'])
    
    # Set default values for existing organizations
    op.execute("""
        UPDATE organizations 
        SET email_settings = '{}'::jsonb 
        WHERE email_settings IS NULL
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_email_threads_last_message_at', table_name='email_threads')
    op.drop_index('idx_email_threads_created_at', table_name='email_threads')
    op.drop_index('idx_email_threads_priority', table_name='email_threads')
    op.drop_index('idx_email_threads_status', table_name='email_threads')
    op.drop_index('idx_email_threads_customer_email', table_name='email_threads')
    op.drop_index('idx_email_threads_conversation', table_name='email_threads')
    op.drop_index('idx_email_threads_organization', table_name='email_threads')
    
    # Drop email_threads table
    op.drop_table('email_threads')
    
    # Remove email_settings column from organizations
    op.drop_column('organizations', 'email_settings')