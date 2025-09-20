"""
Database utility functions
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from pgvector.sqlalchemy import Vector
import logging

# Import database components
from ..models.database import engine, SessionLocal, Base, get_db, create_tables
from ..models.user import Document, KnowledgeSource

logger = logging.getLogger(__name__)

# Export database components
__all__ = ['engine', 'SessionLocal', 'Base', 'get_db', 'create_tables']


class VectorSearchUtils:
    """Utilities for vector similarity search"""
    
    @staticmethod
    def similarity_search(
        db: Session,
        query_embedding: List[float],
        organization_id: str,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        knowledge_source_ids: Optional[List[str]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform vector similarity search
        
        Args:
            db: Database session
            query_embedding: Query vector embedding
            organization_id: Organization ID to filter by
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            knowledge_source_ids: Optional list of knowledge source IDs to filter by
            
        Returns:
            List of (Document, similarity_score) tuples
        """
        try:
            # Build query
            query = db.query(
                Document,
                (1 - Document.embedding.cosine_distance(query_embedding)).label('similarity')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.is_not(None),
                (1 - Document.embedding.cosine_distance(query_embedding)) >= similarity_threshold
            )
            
            # Filter by knowledge source IDs if provided
            if knowledge_source_ids:
                query = query.filter(Document.knowledge_source_id.in_(knowledge_source_ids))
            
            # Order by similarity and limit
            results = query.order_by(
                (1 - Document.embedding.cosine_distance(query_embedding)).desc()
            ).limit(limit).all()
            
            return [(doc, float(similarity)) for doc, similarity in results]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    @staticmethod
    def hybrid_search(
        db: Session,
        query_text: str,
        query_embedding: List[float],
        organization_id: str,
        limit: int = 10,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        knowledge_source_ids: Optional[List[str]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform hybrid search combining vector similarity and text search
        
        Args:
            db: Database session
            query_text: Text query for full-text search
            query_embedding: Query vector embedding
            organization_id: Organization ID to filter by
            limit: Maximum number of results
            vector_weight: Weight for vector similarity score
            text_weight: Weight for text search score
            knowledge_source_ids: Optional list of knowledge source IDs to filter by
            
        Returns:
            List of (Document, combined_score) tuples
        """
        try:
            # Vector similarity subquery
            vector_query = db.query(
                Document.id,
                (1 - Document.embedding.cosine_distance(query_embedding)).label('vector_score')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.is_not(None)
            )
            
            if knowledge_source_ids:
                vector_query = vector_query.filter(Document.knowledge_source_id.in_(knowledge_source_ids))
            
            vector_subquery = vector_query.subquery()
            
            # Text search subquery using pg_trgm
            text_query = db.query(
                Document.id,
                func.similarity(Document.content, query_text).label('text_score')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                func.similarity(Document.content, query_text) > 0.1
            )
            
            if knowledge_source_ids:
                text_query = text_query.filter(Document.knowledge_source_id.in_(knowledge_source_ids))
            
            text_subquery = text_query.subquery()
            
            # Combine results
            combined_query = db.query(
                Document,
                (
                    func.coalesce(vector_subquery.c.vector_score, 0) * vector_weight +
                    func.coalesce(text_subquery.c.text_score, 0) * text_weight
                ).label('combined_score')
            ).outerjoin(
                vector_subquery, Document.id == vector_subquery.c.id
            ).outerjoin(
                text_subquery, Document.id == text_subquery.c.id
            ).filter(
                func.coalesce(vector_subquery.c.vector_score, 0) * vector_weight +
                func.coalesce(text_subquery.c.text_score, 0) * text_weight > 0.1
            ).order_by(
                (
                    func.coalesce(vector_subquery.c.vector_score, 0) * vector_weight +
                    func.coalesce(text_subquery.c.text_score, 0) * text_weight
                ).desc()
            ).limit(limit)
            
            results = combined_query.all()
            return [(doc, float(score)) for doc, score in results]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            # Fallback to vector search only
            return VectorSearchUtils.similarity_search(
                db, query_embedding, organization_id, limit, 0.5, knowledge_source_ids
            )


class DatabaseUtils:
    """General database utility functions"""
    
    @staticmethod
    def get_table_stats(db: Session) -> Dict[str, Any]:
        """Get database table statistics"""
        try:
            stats = {}
            
            # Get table row counts
            tables = [
                'organizations', 'users', 'assistants', 'knowledge_sources',
                'documents', 'conversations', 'messages', 'subscriptions', 'audit_logs'
            ]
            
            for table in tables:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[f"{table}_count"] = result.scalar()
            
            # Get database size
            result = db.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            stats["database_size"] = result.scalar()
            
            # Get vector index stats
            result = db.execute(text("""
                SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
                FROM pg_stat_user_indexes 
                WHERE indexname LIKE '%embedding%'
            """))
            stats["vector_indexes"] = [dict(row) for row in result]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return {}
    
    @staticmethod
    def optimize_vector_index(db: Session, table_name: str = "documents") -> bool:
        """Optimize vector index performance"""
        try:
            # Analyze table for better query planning
            db.execute(text(f"ANALYZE {table_name}"))
            
            # Update index statistics
            db.execute(text(f"REINDEX INDEX idx_{table_name}_embedding_cosine"))
            
            db.commit()
            logger.info(f"Optimized vector index for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize vector index: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def cleanup_old_data(db: Session, days: int = 90) -> Dict[str, int]:
        """Clean up old data based on retention policy"""
        try:
            cleanup_stats = {}
            
            # Clean up old audit logs
            result = db.execute(text("""
                DELETE FROM audit_logs 
                WHERE created_at < NOW() - INTERVAL '%s days'
                AND risk_level = 'low'
            """), (days,))
            cleanup_stats["audit_logs_deleted"] = result.rowcount
            
            # Clean up old conversations (closed for more than retention period)
            result = db.execute(text("""
                DELETE FROM conversations 
                WHERE status = 'closed' 
                AND ended_at < NOW() - INTERVAL '%s days'
            """), (days,))
            cleanup_stats["conversations_deleted"] = result.rowcount
            
            db.commit()
            logger.info(f"Cleaned up old data: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            db.rollback()
            return {}
    
    @staticmethod
    def get_performance_metrics(db: Session) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            metrics = {}
            
            # Connection stats
            result = db.execute(text("""
                SELECT state, count(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database()
                GROUP BY state
            """))
            metrics["connections"] = dict(result)
            
            # Slow queries
            result = db.execute(text("""
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements 
                WHERE mean_time > 1000
                ORDER BY mean_time DESC 
                LIMIT 10
            """))
            metrics["slow_queries"] = [dict(row) for row in result]
            
            # Index usage
            result = db.execute(text("""
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC 
                LIMIT 10
            """))
            metrics["index_usage"] = [dict(row) for row in result]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}