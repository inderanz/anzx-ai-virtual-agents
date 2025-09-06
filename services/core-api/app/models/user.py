"""
Comprehensive database models for ANZx.ai platform
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, 
    Numeric, Index, UniqueConstraint, CheckConstraint, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
import uuid

from .database import Base


class Organization(Base):
    """Organization model with subscription and compliance tracking"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Location and compliance
    region = Column(String(10), default="AU")  # AU, NZ, US, etc.
    timezone = Column(String(50), default="Australia/Sydney")
    
    # Subscription
    subscription_plan = Column(String(50), default="freemium")  # freemium, pro, enterprise
    subscription_status = Column(String(50), default="active")  # active, cancelled, suspended
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Usage limits and tracking
    monthly_message_limit = Column(Integer, default=1000)
    monthly_message_count = Column(Integer, default=0)
    monthly_token_limit = Column(Integer, default=100000)
    monthly_token_count = Column(Integer, default=0)
    
    # Settings and configuration
    settings = Column(JSON, default=dict)
    branding = Column(JSON, default=dict)  # Logo, colors, etc.
    email_settings = Column(JSON, default=dict)  # Email integration settings
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    assistants = relationship("Assistant", back_populates="organization", cascade="all, delete-orphan")
    knowledge_sources = relationship("KnowledgeSource", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization")
    subscriptions = relationship("Subscription", back_populates="organization", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_organizations_stripe_customer', 'stripe_customer_id'),
        Index('idx_organizations_subscription_status', 'subscription_status'),
        Index('idx_organizations_region', 'region'),
    )


class User(Base):
    """User model with enhanced profile and preferences"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    
    # Profile information
    display_name = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    role = Column(String(50), default="user")  # user, admin, super_admin
    
    # Status and activity
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Privacy and compliance
    privacy_consent = Column(Boolean, default=False)
    privacy_consent_date = Column(DateTime, nullable=True)
    marketing_consent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_firebase_uid', 'firebase_uid'),
        Index('idx_users_email', 'email'),
        Index('idx_users_organization_role', 'organization_id', 'role'),
        Index('idx_users_active', 'is_active'),
    )


class Assistant(Base):
    """AI Assistant model with configuration and performance tracking"""
    __tablename__ = "assistants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # support, admin, content, insights
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Configuration
    system_prompt = Column(Text, nullable=True)
    model_config = Column(JSON, default=dict)  # Temperature, max_tokens, etc.
    tools_config = Column(JSON, default=dict)  # Available tools and settings
    knowledge_sources = Column(ARRAY(UUID), default=list)  # Linked knowledge sources
    
    # Status and deployment
    is_active = Column(Boolean, default=True)
    deployment_status = Column(String(50), default="draft")  # draft, deployed, archived
    version = Column(String(50), default="1.0.0")
    
    # Performance metrics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployed_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="assistants")
    conversations = relationship("Conversation", back_populates="assistant")
    
    # Indexes
    __table_args__ = (
        Index('idx_assistants_organization_type', 'organization_id', 'type'),
        Index('idx_assistants_active', 'is_active'),
        Index('idx_assistants_deployment_status', 'deployment_status'),
    )


class KnowledgeSource(Base):
    """Knowledge source model for RAG system"""
    __tablename__ = "knowledge_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Source information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # file, url, text, api
    source_url = Column(String(1000), nullable=True)
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_progress = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    
    # Content metadata
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(100), nullable=True)
    chunk_count = Column(Integer, default=0)
    
    # Configuration
    chunking_config = Column(JSON, default=dict)
    embedding_model = Column(String(100), default="text-embedding-004")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="knowledge_sources")
    documents = relationship("Document", back_populates="knowledge_source", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_sources_organization', 'organization_id'),
        Index('idx_knowledge_sources_status', 'status'),
        Index('idx_knowledge_sources_type', 'type'),
    )


class Document(Base):
    """Document chunks with vector embeddings"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # Vector embedding (768 dimensions for text-embedding-004)
    embedding = Column(Vector(768), nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Page number, section, etc.
    token_count = Column(Integer, default=0)
    
    # Search optimization
    content_hash = Column(String(64), nullable=True)  # For deduplication
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_knowledge_source', 'knowledge_source_id'),
        Index('idx_documents_chunk_index', 'knowledge_source_id', 'chunk_index'),
        Index('idx_documents_content_hash', 'content_hash'),
        # Vector similarity index (will be created in migration)
        Index('idx_documents_embedding_cosine', 'embedding', postgresql_using='ivfflat', 
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )


class Conversation(Base):
    """Conversation model with enhanced tracking"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Can be anonymous
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"), nullable=False)
    
    # Channel and session
    channel = Column(String(50), default="widget")  # widget, email, api, slack
    session_id = Column(String(255), nullable=True)
    
    # Status and resolution
    status = Column(String(50), default="active")  # active, resolved, escalated, closed
    resolution_status = Column(String(50), nullable=True)  # resolved, escalated, timeout
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating
    
    # Performance metrics
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Numeric(10, 6), default=0)
    average_response_time = Column(Float, default=0.0)
    
    # Metadata and context
    metadata = Column(JSON, default=dict)
    context = Column(JSON, default=dict)  # Conversation context for AI
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    assistant = relationship("Assistant", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversations_organization', 'organization_id'),
        Index('idx_conversations_user', 'user_id'),
        Index('idx_conversations_assistant', 'assistant_id'),
        Index('idx_conversations_status', 'status'),
        Index('idx_conversations_channel', 'channel'),
        Index('idx_conversations_created_at', 'created_at'),
    )


class Message(Base):
    """Message model with enhanced metadata and performance tracking"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system, tool
    
    # AI generation metadata
    model = Column(String(100), nullable=True)  # Model used for generation
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost = Column(Numeric(10, 6), default=0)
    latency_ms = Column(Integer, default=0)
    
    # Tool usage
    tool_calls = Column(JSON, default=list)  # Tools called during generation
    tool_results = Column(JSON, default=list)  # Results from tool calls
    
    # Quality and feedback
    confidence_score = Column(Float, nullable=True)  # AI confidence in response
    feedback_rating = Column(Integer, nullable=True)  # User feedback (1-5)
    feedback_comment = Column(Text, nullable=True)
    
    # Citations and sources
    citations = Column(JSON, default=list)  # Knowledge sources cited
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_conversation', 'conversation_id'),
        Index('idx_messages_role', 'role'),
        Index('idx_messages_created_at', 'created_at'),
        Index('idx_messages_model', 'model'),
    )


class Subscription(Base):
    """Subscription and billing model"""
    __tablename__ = "subscriptions"
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True)
    
    # Stripe integration
    stripe_customer_id = Column(String(255), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    # Plan details
    plan = Column(String(50), nullable=False)  # freemium, pro, enterprise
    status = Column(String(50), default="active")  # active, cancelled, past_due, unpaid
    
    # Billing cycle
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    # Usage tracking
    usage_counters = Column(JSON, default=dict)  # Current period usage
    usage_limits = Column(JSON, default=dict)  # Plan limits
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    
    # Indexes
    __table_args__ = (
        Index('idx_subscriptions_stripe_customer', 'stripe_customer_id'),
        Index('idx_subscriptions_stripe_subscription', 'stripe_subscription_id'),
        Index('idx_subscriptions_status', 'status'),
    )


class AuditLog(Base):
    """Audit log for compliance and security tracking"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    outcome = Column(String(50), nullable=False)  # success, failure, blocked
    
    # Actor information
    user_id = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # Event context
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, default=dict)
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_event_type', 'event_type'),
        Index('idx_audit_logs_user', 'user_id'),
        Index('idx_audit_logs_organization', 'organization_id'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_risk_level', 'risk_level'),
        Index('idx_audit_logs_outcome', 'outcome'),
    )

cl
ass ChatWidget(Base):
    """Chat widget configuration for embeddable widgets"""
    __tablename__ = "chat_widgets"
    
    id = Column(String(32), primary_key=True)  # URL-safe token
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"))
    api_key = Column(String(64), nullable=False, unique=True)
    allowed_domains = Column(JSON, default=list)  # List of allowed domains
    widget_settings = Column(JSON, default=dict)  # Theme, colors, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization")
    assistant = relationship("Assistant")
    conversations = relationship("Conversation", back_populates="widget")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_widgets_organization', 'organization_id'),
        Index('idx_chat_widgets_assistant', 'assistant_id'),
        Index('idx_chat_widgets_active', 'is_active'),
        Index('idx_chat_widgets_api_key', 'api_key'),
    )


class EmailThread(Base):
    """Email thread management for support email integration"""
    __tablename__ = "email_threads"
    
    id = Column(String(32), primary_key=True)  # Generated thread ID
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    subject = Column(String(500), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255))
    status = Column(String(50), default="new")  # new, active, responded, escalated, closed
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    message_references = Column(Text)  # Email message IDs for threading
    last_message_id = Column(String(255))
    last_message_at = Column(DateTime)
    last_response_at = Column(DateTime)
    response_count = Column(Integer, default=0)
    escalated_at = Column(DateTime)
    escalation_reason = Column(Text)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
    conversation = relationship("Conversation")
    
    # Indexes
    __table_args__ = (
        Index('idx_email_threads_organization', 'organization_id'),
        Index('idx_email_threads_conversation', 'conversation_id'),
        Index('idx_email_threads_customer_email', 'customer_email'),
        Index('idx_email_threads_status', 'status'),
        Index('idx_email_threads_priority', 'priority'),
        Index('idx_email_threads_created_at', 'created_at'),
        Index('idx_email_threads_last_message_at', 'last_message_at'),
    )
cl
ass MCPServer(Base):
    """MCP Server configuration and status"""
    __tablename__ = "mcp_servers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    config = Column(JSON, nullable=False)  # Server configuration
    status = Column(String(50), default="registered")  # registered, running, stopped, error
    is_active = Column(Boolean, default=True)
    
    # Runtime information
    pid = Column(Integer)
    started_at = Column(DateTime)
    last_health_check = Column(DateTime)
    restart_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Capabilities
    capabilities = Column(JSON, default=list)  # List of capabilities
    tools_count = Column(Integer, default=0)
    resources_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
    tools = relationship("MCPTool", back_populates="server", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_mcp_servers_organization', 'organization_id'),
        Index('idx_mcp_servers_name', 'name'),
        Index('idx_mcp_servers_status', 'status'),
        Index('idx_mcp_servers_active', 'is_active'),
        UniqueConstraint('organization_id', 'name', name='uq_mcp_servers_org_name'),
    )


class MCPTool(Base):
    """MCP Tool definition and metadata"""
    __tablename__ = "mcp_tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("mcp_servers.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Tool definition
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # communication, finance, storage, etc.
    
    # Tool schema
    input_schema = Column(JSON, nullable=False)  # JSON schema for input parameters
    output_schema = Column(JSON)  # JSON schema for output (optional)
    
    # Configuration
    is_enabled = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    timeout_seconds = Column(Integer, default=30)
    rate_limit_per_minute = Column(Integer, default=60)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    average_execution_time_ms = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    
    # Security
    security_policy = Column(JSON, default=dict)
    allowed_roles = Column(JSON, default=list)  # List of roles that can use this tool
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    server = relationship("MCPServer", back_populates="tools")
    organization = relationship("Organization")
    executions = relationship("MCPToolExecution", back_populates="tool", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_mcp_tools_server', 'server_id'),
        Index('idx_mcp_tools_organization', 'organization_id'),
        Index('idx_mcp_tools_name', 'name'),
        Index('idx_mcp_tools_category', 'category'),
        Index('idx_mcp_tools_enabled', 'is_enabled'),
        UniqueConstraint('server_id', 'name', name='uq_mcp_tools_server_name'),
    )


class MCPToolExecution(Base):
    """MCP Tool execution log and results"""
    __tablename__ = "mcp_tool_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp_tools.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    
    # Execution details
    input_parameters = Column(JSON, nullable=False)
    output_result = Column(JSON)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed, timeout
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    error_code = Column(String(100))
    retry_count = Column(Integer, default=0)
    
    # Security and approval
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_reason = Column(Text)
    
    # Resource usage
    memory_usage_mb = Column(Integer)
    cpu_usage_percent = Column(Float)
    network_requests = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tool = relationship("MCPTool", back_populates="executions")
    organization = relationship("Organization")
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])
    conversation = relationship("Conversation")
    
    # Indexes
    __table_args__ = (
        Index('idx_mcp_executions_tool', 'tool_id'),
        Index('idx_mcp_executions_organization', 'organization_id'),
        Index('idx_mcp_executions_user', 'user_id'),
        Index('idx_mcp_executions_conversation', 'conversation_id'),
        Index('idx_mcp_executions_status', 'status'),
        Index('idx_mcp_executions_started_at', 'started_at'),
    )