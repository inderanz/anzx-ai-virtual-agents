"""
Knowledge Base Management Service
Orchestrates document processing, embedding, and search operations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import KnowledgeSource, Document, Organization
from .document_processor import document_processor
from .vector_search_service import vector_search_service
from ..middleware.usage_tracking import usage_tracker

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    High-level knowledge management service
    
    Orchestrates:
    - Document processing pipeline
    - Vector embedding generation
    - Search operations
    - Knowledge source lifecycle management
    """
    
    def __init__(self):
        self.document_processor = document_processor
        self.vector_search = vector_search_service
    
    async def create_knowledge_source(
        self,
        db: Session,
        organization_id: str,
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create and process a new knowledge source
        
        Args:
            db: Database session
            organization_id: Organization ID
            source_data: Source configuration and content
            
        Returns:
            Created knowledge source information
        """
        try:
            # Validate organization
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            # Process the document source
            processing_result = await self.document_processor.process_document_source(
                db=db,
                organization_id=organization_id,
                source_data=source_data
            )
            
            if not processing_result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Document processing failed"
                )
            
            source_id = processing_result["source_id"]
            
            # Generate embeddings for the processed documents
            embedding_result = await self.vector_search.embed_documents(
                db=db,
                source_id=source_id,
                organization_id=organization_id
            )
            
            # Track usage
            await usage_tracker.track_knowledge_processing(
                db=db,
                organization_id=organization_id,
                documents_processed=processing_result.get("documents_created", 0),
                processing_time_ms=processing_result.get("processing_time_ms", 0)
            )
            
            return {
                "source_id": source_id,
                "status": processing_result["status"],
                "documents_created": processing_result.get("documents_created", 0),
                "chunks_created": processing_result.get("chunks_created", 0),
                "embeddings_generated": embedding_result.get("documents_processed", 0),
                "processing_time_ms": processing_result.get("processing_time_ms", 0),
                "embedding_time_ms": embedding_result.get("processing_time_ms", 0)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Knowledge source creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create knowledge source: {str(e)}"
            )
    
    async def get_knowledge_sources(
        self,
        db: Session,
        organization_id: str,
        status_filter: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all knowledge sources for an organization"""
        try:
            query = db.query(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id
            )
            
            if status_filter:
                query = query.filter(KnowledgeSource.status == status_filter)
            
            if type_filter:
                query = query.filter(KnowledgeSource.type == type_filter)
            
            sources = query.order_by(KnowledgeSource.created_at.desc()).all()
            
            result = []
            for source in sources:
                # Get document count
                doc_count = db.query(Document).filter(Document.source_id == source.id).count()
                
                # Get embedding count
                embedded_count = db.query(Document).filter(
                    Document.source_id == source.id,
                    Document.embedding.isnot(None)
                ).count()
                
                result.append({
                    "id": str(source.id),
                    "name": source.name,
                    "type": source.type,
                    "status": source.status,
                    "source_url": source.source_url,
                    "document_count": doc_count,
                    "embedded_count": embedded_count,
                    "embedding_coverage": round((embedded_count / doc_count * 100) if doc_count > 0 else 0, 1),
                    "created_at": source.created_at.isoformat(),
                    "processed_at": source.processed_at.isoformat() if source.processed_at else None,
                    "metadata": source.metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get knowledge sources: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve knowledge sources"
            )
    
    async def get_knowledge_source(
        self,
        db: Session,
        source_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific knowledge source"""
        try:
            source = db.query(KnowledgeSource).filter(
                KnowledgeSource.id == source_id,
                KnowledgeSource.organization_id == organization_id
            ).first()
            
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge source not found"
                )
            
            # Get documents
            documents = db.query(Document).filter(Document.source_id == source_id).all()
            
            # Calculate statistics
            total_docs = len(documents)
            embedded_docs = sum(1 for doc in documents if doc.embedding is not None)
            total_content_length = sum(len(doc.content) for doc in documents)
            
            # Get sample documents
            sample_docs = []
            for doc in documents[:5]:  # First 5 documents
                sample_docs.append({
                    "id": str(doc.id),
                    "chunk_id": doc.chunk_id,
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "content_length": len(doc.content),
                    "has_embedding": doc.embedding is not None,
                    "metadata": doc.metadata
                })
            
            return {
                "id": str(source.id),
                "name": source.name,
                "type": source.type,
                "status": source.status,
                "source_url": source.source_url,
                "created_at": source.created_at.isoformat(),
                "processed_at": source.processed_at.isoformat() if source.processed_at else None,
                "metadata": source.metadata,
                "statistics": {
                    "total_documents": total_docs,
                    "embedded_documents": embedded_docs,
                    "embedding_coverage_percent": round((embedded_docs / total_docs * 100) if total_docs > 0 else 0, 1),
                    "total_content_length": total_content_length,
                    "average_chunk_size": round(total_content_length / total_docs) if total_docs > 0 else 0
                },
                "sample_documents": sample_docs
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get knowledge source: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve knowledge source"
            )
    
    async def update_knowledge_source(
        self,
        db: Session,
        source_id: str,
        organization_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update knowledge source metadata"""
        try:
            source = db.query(KnowledgeSource).filter(
                KnowledgeSource.id == source_id,
                KnowledgeSource.organization_id == organization_id
            ).first()
            
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge source not found"
                )
            
            # Update allowed fields
            if "name" in update_data:
                source.name = update_data["name"]
            
            if "metadata" in update_data:
                source.metadata.update(update_data["metadata"])
            
            db.commit()
            
            return {
                "id": str(source.id),
                "name": source.name,
                "status": source.status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update knowledge source: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update knowledge source"
            )
    
    async def delete_knowledge_source(
        self,
        db: Session,
        source_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Delete a knowledge source and all its documents"""
        try:
            source = db.query(KnowledgeSource).filter(
                KnowledgeSource.id == source_id,
                KnowledgeSource.organization_id == organization_id
            ).first()
            
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge source not found"
                )
            
            # Count documents before deletion
            doc_count = db.query(Document).filter(Document.source_id == source_id).count()
            
            # Delete documents first (due to foreign key constraint)
            db.query(Document).filter(Document.source_id == source_id).delete()
            
            # Delete the source
            db.delete(source)
            db.commit()
            
            return {
                "source_id": source_id,
                "documents_deleted": doc_count,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete knowledge source: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete knowledge source"
            )
    
    async def reprocess_knowledge_source(
        self,
        db: Session,
        source_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Reprocess a knowledge source (for URL sources)"""
        try:
            # Reprocess documents
            processing_result = await self.document_processor.reprocess_source(
                db=db,
                source_id=source_id,
                organization_id=organization_id
            )
            
            if processing_result["success"]:
                # Generate embeddings for new documents
                embedding_result = await self.vector_search.embed_documents(
                    db=db,
                    source_id=source_id,
                    organization_id=organization_id
                )
                
                return {
                    "source_id": source_id,
                    "status": "completed",
                    "documents_created": processing_result.get("documents_created", 0),
                    "chunks_created": processing_result.get("chunks_created", 0),
                    "embeddings_generated": embedding_result.get("documents_processed", 0),
                    "reprocessed_at": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Reprocessing failed: {processing_result.get('error', 'Unknown error')}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to reprocess knowledge source: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reprocess knowledge source"
            )
    
    async def search_knowledge_base(
        self,
        db: Session,
        organization_id: str,
        query: str,
        search_type: str = "hybrid",
        max_results: int = 10,
        source_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search the organization's knowledge base
        
        Args:
            db: Database session
            organization_id: Organization ID
            query: Search query
            search_type: Type of search (semantic, keyword, hybrid)
            max_results: Maximum results to return
            source_filter: Filter by knowledge source ID
            
        Returns:
            Search results with metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Perform search based on type
            if search_type == "semantic":
                results = await self.vector_search.semantic_search(
                    db=db,
                    organization_id=organization_id,
                    query=query,
                    max_results=max_results,
                    source_filter=source_filter
                )
            elif search_type == "keyword":
                results = await self.vector_search.keyword_search(
                    db=db,
                    organization_id=organization_id,
                    query=query,
                    max_results=max_results,
                    source_filter=source_filter
                )
            else:  # hybrid
                results = await self.vector_search.hybrid_search(
                    db=db,
                    organization_id=organization_id,
                    query=query,
                    max_results=max_results,
                    source_filter=source_filter
                )
            
            end_time = datetime.utcnow()
            search_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Format results for API response
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "document_id": result["document_id"],
                    "source_id": result["source_id"],
                    "source_name": result["source_name"],
                    "content": result["content"],
                    "score": result.get("combined_score", result.get("similarity_score", result.get("relevance_score", 0))),
                    "metadata": result["metadata"],
                    "chunk_id": result["chunk_id"]
                })
            
            # Track search usage
            await usage_tracker.track_search_query(
                db=db,
                organization_id=organization_id,
                query=query,
                results_count=len(results),
                search_time_ms=search_time_ms
            )
            
            return {
                "query": query,
                "search_type": search_type,
                "results": formatted_results,
                "total_results": len(results),
                "search_time_ms": search_time_ms,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Search failed"
            )
    
    async def get_knowledge_analytics(
        self,
        db: Session,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive knowledge base analytics"""
        try:
            # Get processing statistics
            processing_stats = await self.document_processor.get_processing_stats(
                db=db,
                organization_id=organization_id
            )
            
            # Get search analytics
            search_analytics = await self.vector_search.get_search_analytics(
                db=db,
                organization_id=organization_id
            )
            
            # Combine analytics
            return {
                "processing": processing_stats,
                "search": search_analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve analytics"
            )
    
    async def health_check(self, db: Session) -> Dict[str, Any]:
        """Check knowledge service health"""
        try:
            # Test database connectivity
            db.execute("SELECT 1")
            
            # Check if pgvector extension is available
            try:
                db.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                pgvector_available = True
            except:
                pgvector_available = False
            
            return {
                "status": "healthy",
                "database_connected": True,
                "pgvector_available": pgvector_available,
                "document_processor_ready": self.document_processor is not None,
                "vector_search_ready": self.vector_search is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
knowledge_service = KnowledgeService()