"""Add chat widgets tables

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_widgets table
    op.create_table('chat_widgets',
        sa.Column('id', sa.String(32), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('api_key', sa.String(64), nullable=False),
        sa.Column('allowed_domains', postgresql.JSON(), nullable=True),
        sa.Column('widget_settings', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assistant_id'], ['assistants.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key')
    )
    
    # Add widget_id column to conversations table
    op.add_column('conversations', sa.Column('widget_id', sa.String(32), nullable=True))
    op.create_foreign_key('fk_conversations_widget_id', 'conversations', 'chat_widgets', ['widget_id'], ['id'])
    
    # Create indexes for performance
    op.create_index('ix_chat_widgets_organization_id', 'chat_widgets', ['organization_id'])
    op.create_index('ix_chat_widgets_assistant_id', 'chat_widgets', ['assistant_id'])
    op.create_index('ix_chat_widgets_is_active', 'chat_widgets', ['is_active'])
    op.create_index('ix_conversations_widget_id', 'conversations', ['widget_id'])


def downgrade():
    # Remove indexes
    op.drop_index('ix_conversations_widget_id', table_name='conversations')
    op.drop_index('ix_chat_widgets_is_active', table_name='chat_widgets')
    op.drop_index('ix_chat_widgets_assistant_id', table_name='chat_widgets')
    op.drop_index('ix_chat_widgets_organization_id', table_name='chat_widgets')
    
    # Remove foreign key and column
    op.drop_constraint('fk_conversations_widget_id', 'conversations', type_='foreignkey')
    op.drop_column('conversations', 'widget_id')
    
    # Drop chat_widgets table
    op.drop_table('chat_widgets')