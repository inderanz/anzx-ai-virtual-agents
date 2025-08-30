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