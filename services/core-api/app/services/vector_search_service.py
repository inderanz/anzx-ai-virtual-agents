"""
Vector Embedding and Search System
Handles embedding generation, vector storage, and hybrid search
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

try:
    from vertexai.language_models import TextEmbeddingModel
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from pgvector.sqlalchemy import Vector
except ImportError as e:
    logging.warning(f"Vector search dependencies not installed: {e}")
    # Mock classes for development
    class TextEmbeddingModel:
        @classmethod
        def from_pretrained(cls, model_name): return cls()
        def get_embeddings(self, texts): return [type('obj', (object,), {'values': [0.1] * 768})() for _ in texts]
    import numpy as np
    class Vector:
        pass

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from ..models.user import Document, KnowledgeSource, Organization
from ..config.vertex_ai import vertex_ai_config

logger = logging.getLogger(__name__)


class VectorSearchService:
    """
    Vector embedding and search service using Vertex AI and pgvector
    
    Features:
    - Vertex AI Text Embeddings API integration
    - pgvector storage with indexing
    - Hybrid search (semantic + keyword)
    - Citation tracking and reranking
    - Batch processing for performance
    """
    
    def __init__(self):
        self.config = vertex_ai_config
        self.embedding_model_name = self.config.EMBEDDING_CONFIG["model"]
        self.embedding_dimensions = self.config.EMBEDDING_CONFIG["dimensions"]
        self.batch_size = self.config.EMBEDDING_CONFIG["batch_size"]
        
        # Initialize embedding model
        self._embedding_model = None
        self._initialize_embedding_model()
        
        # Search configuration
        self.max_results = self.config.SEARCH_CONFIG["max_results"]
        self.similarity_threshold = self.config.SEARCH_CONFIG["similarity_threshold"]
        self.rerank_results = self.config.SEARCH_CONFIG["rerank_results"]
    
    def _initialize_embedding_model(self):
        """Initialize Vertex AI embedding model"""
        try:
            self._embedding_model = TextEmbeddingModel.from_pretrained(self.embedding_model_name)
            logger.info(f"Initialized embedding model: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
    
    async def generate_embeddings(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            task_type: Task type for embeddings
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self._embedding_model:
                raise ValueError("Embedding model not initialized")
            
            if not texts:
                return []
            
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                # Generate embeddings for batch
                embeddings = self._embedding_model.get_embeddings(
                    batch,
                    task_type=task_type
                )
                
                # Extract embedding values
                batch_embeddings = [emb.values for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
                
                # Add small delay to avoid rate limiting
                if i + self.batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    async def embed_documents(
        self,
        db: Session,
        source_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Generate and store embeddings for all documents in a source
        
        Args:
            db: Database session
            source_id: Knowledge source ID
            organization_id: Organization ID
            
        Returns:
            Embedding result
        """
        try:
            start_time = datetime.utcnow()
            
            # Get documents without embeddings
            documents = db.query(Document).join(KnowledgeSource).filter(
                Document.source_id == source_id,
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.is_(None)
            ).all()
            
            if not documents:
                return {
                    "success": True,
                    "documents_processed": 0,
                    "message": "No documents need embedding"
                }
            
            # Extract text content
            texts = [doc.content for doc in documents]
            
            # Generate embeddings
            embeddings = await self.generate_embeddings(texts, "RETRIEVAL_DOCUMENT")
            
            # Store embeddings
            documents_updated = 0
            for doc, embedding in zip(documents, embeddings):
                doc.embedding = embedding
                documents_updated += 1
            
            db.commit()
            
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            logger.info(f"Embedded {documents_updated} documents in {processing_time_ms}ms")
            
            return {
                "success": True,
                "documents_processed": documents_updated,
                "processing_time_ms": processing_time_ms,
                "embedding_model": self.embedding_model_name,
                "embedding_dimensions": self.embedding_dimensions
            }
            
        except Exception as e:
            logger.error(f"Document embedding failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "documents_processed": 0
            }
    
    async def semantic_search(
        self,
        db: Session,
        organization_id: str,
        query: str,
        max_results: int = None,
        source_filter: Optional[str] = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector similarity
        
        Args:
            db: Database session
            organization_id: Organization ID
            query: Search query
            max_results: Maximum results to return
            source_filter: Filter by knowledge source ID
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with similarity scores
        """
        try:
            max_results = max_results or self.max_results
            similarity_threshold = similarity_threshold or self.similarity_threshold
            
            # Generate query embedding
            query_embeddings = await self.generate_embeddings([query], "RETRIEVAL_QUERY")
            if not query_embeddings:
                return []
            
            query_embedding = query_embeddings[0]
            
            # Build SQL query for vector similarity search
            base_query = db.query(
                Document,
                KnowledgeSource.name.label('source_name'),
                func.cosine_distance(Document.embedding, query_embedding).label('distance')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.isnot(None)
            )
            
            # Apply source filter
            if source_filter:
                base_query = base_query.filter(KnowledgeSource.id == source_filter)
            
            # Order by similarity and limit results
            results = base_query.order_by(
                func.cosine_distance(Document.embedding, query_embedding)
            ).limit(max_results).all()
            
            # Format results
            search_results = []
            for doc, source_name, distance in results:
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= similarity_threshold:
                    search_results.append({
                        "document_id": str(doc.id),
                        "source_id": str(doc.source_id),
                        "source_name": source_name,
                        "content": doc.content,
                        "similarity_score": float(similarity),
                        "metadata": doc.metadata,
                        "chunk_id": doc.chunk_id
                    })
            
            logger.info(f"Semantic search returned {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def keyword_search(
        self,
        db: Session,
        organization_id: str,
        query: str,
        max_results: int = None,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based full-text search
        
        Args:
            db: Database session
            organization_id: Organization ID
            query: Search query
            max_results: Maximum results to return
            source_filter: Filter by knowledge source ID
            
        Returns:
            List of search results with relevance scores
        """
        try:
            max_results = max_results or self.max_results
            
            # Build full-text search query
            base_query = db.query(
                Document,
                KnowledgeSource.name.label('source_name'),
                func.ts_rank(
                    func.to_tsvector('english', Document.content),
                    func.plainto_tsquery('english', query)
                ).label('rank')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                func.to_tsvector('english', Document.content).match(query)
            )
            
            # Apply source filter
            if source_filter:
                base_query = base_query.filter(KnowledgeSource.id == source_filter)
            
            # Order by relevance and limit results
            results = base_query.order_by(
                func.ts_rank(
                    func.to_tsvector('english', Document.content),
                    func.plainto_tsquery('english', query)
                ).desc()
            ).limit(max_results).all()
            
            # Format results
            search_results = []
            for doc, source_name, rank in results:
                search_results.append({
                    "document_id": str(doc.id),
                    "source_id": str(doc.source_id),
                    "source_name": source_name,
                    "content": doc.content,
                    "relevance_score": float(rank),
                    "metadata": doc.metadata,
                    "chunk_id": doc.chunk_id
                })
            
            logger.info(f"Keyword search returned {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    async def hybrid_search(
        self,
        db: Session,
        organization_id: str,
        query: str,
        max_results: int = None,
        source_filter: Optional[str] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            db: Database session
            organization_id: Organization ID
            query: Search query
            max_results: Maximum results to return
            source_filter: Filter by knowledge source ID
            semantic_weight: Weight for semantic search results
            keyword_weight: Weight for keyword search results
            
        Returns:
            List of reranked search results
        """
        try:
            max_results = max_results or self.max_results
            
            # Perform both searches in parallel
            semantic_task = self.semantic_search(
                db, organization_id, query, max_results * 2, source_filter
            )
            keyword_task = self.keyword_search(
                db, organization_id, query, max_results * 2, source_filter
            )
            
            semantic_results, keyword_results = await asyncio.gather(
                semantic_task, keyword_task
            )
            
            # Combine and rerank results
            combined_results = self._combine_search_results(
                semantic_results, keyword_results, semantic_weight, keyword_weight
            )
            
            # Apply reranking if enabled
            if self.rerank_results:
                combined_results = await self._rerank_results(query, combined_results)
            
            # Limit final results
            final_results = combined_results[:max_results]
            
            logger.info(f"Hybrid search returned {len(final_results)} results for query: {query[:50]}...")
            return final_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def _combine_search_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[Dict[str, Any]]:
        """Combine and score results from semantic and keyword search"""
        try:
            # Create document ID to result mapping
            all_results = {}
            
            # Add semantic results
            for result in semantic_results:
                doc_id = result["document_id"]
                result["semantic_score"] = result.get("similarity_score", 0)
                result["keyword_score"] = 0
                all_results[doc_id] = result
            
            # Add/update with keyword results
            for result in keyword_results:
                doc_id = result["document_id"]
                if doc_id in all_results:
                    all_results[doc_id]["keyword_score"] = result.get("relevance_score", 0)
                else:
                    result["semantic_score"] = 0
                    result["keyword_score"] = result.get("relevance_score", 0)
                    all_results[doc_id] = result
            
            # Calculate combined scores
            for result in all_results.values():
                # Normalize scores to 0-1 range
                semantic_norm = min(result["semantic_score"], 1.0)
                keyword_norm = min(result["keyword_score"] / 10.0, 1.0)  # Assuming max rank ~10
                
                result["combined_score"] = (
                    semantic_weight * semantic_norm + 
                    keyword_weight * keyword_norm
                )
            
            # Sort by combined score
            sorted_results = sorted(
                all_results.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            return sorted_results
            
        except Exception as e:
            logger.error(f"Result combination failed: {e}")
            return semantic_results + keyword_results
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using additional relevance signals"""
        try:
            # Simple reranking based on query term frequency
            query_terms = query.lower().split()
            
            for result in results:
                content_lower = result["content"].lower()
                
                # Count query term matches
                term_matches = sum(
                    content_lower.count(term) for term in query_terms
                )
                
                # Boost score based on term frequency
                term_boost = min(term_matches * 0.1, 0.5)
                result["combined_score"] += term_boost
                
                # Boost recent content (if timestamp available)
                if "created_at" in result.get("metadata", {}):
                    # Add recency boost (simplified)
                    result["combined_score"] += 0.05
            
            # Re-sort by updated scores
            reranked_results = sorted(
                results,
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Result reranking failed: {e}")
            return results
    
    async def get_similar_documents(
        self,
        db: Session,
        document_id: str,
        organization_id: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        try:
            # Get the reference document
            ref_doc = db.query(Document).join(KnowledgeSource).filter(
                Document.id == document_id,
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.isnot(None)
            ).first()
            
            if not ref_doc:
                return []
            
            # Find similar documents
            results = db.query(
                Document,
                KnowledgeSource.name.label('source_name'),
                func.cosine_distance(Document.embedding, ref_doc.embedding).label('distance')
            ).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                Document.id != document_id,
                Document.embedding.isnot(None)
            ).order_by(
                func.cosine_distance(Document.embedding, ref_doc.embedding)
            ).limit(max_results).all()
            
            # Format results
            similar_docs = []
            for doc, source_name, distance in results:
                similarity = 1 - distance
                similar_docs.append({
                    "document_id": str(doc.id),
                    "source_id": str(doc.source_id),
                    "source_name": source_name,
                    "content": doc.content[:200] + "...",  # Truncate for preview
                    "similarity_score": float(similarity),
                    "metadata": doc.metadata
                })
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Similar document search failed: {e}")
            return []
    
    async def get_search_analytics(
        self,
        db: Session,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get search and embedding analytics"""
        try:
            # Count documents with embeddings
            embedded_docs = db.query(Document).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id,
                Document.embedding.isnot(None)
            ).count()
            
            # Count total documents
            total_docs = db.query(Document).join(KnowledgeSource).filter(
                KnowledgeSource.organization_id == organization_id
            ).count()
            
            # Get embedding coverage by source
            source_stats = db.query(
                KnowledgeSource.name,
                func.count(Document.id).label('total_docs'),
                func.count(Document.embedding).label('embedded_docs')
            ).join(Document).filter(
                KnowledgeSource.organization_id == organization_id
            ).group_by(KnowledgeSource.name).all()
            
            source_breakdown = []
            for name, total, embedded in source_stats:
                coverage = (embedded / total * 100) if total > 0 else 0
                source_breakdown.append({
                    "source_name": name,
                    "total_documents": total,
                    "embedded_documents": embedded,
                    "coverage_percent": round(coverage, 1)
                })
            
            return {
                "total_documents": total_docs,
                "embedded_documents": embedded_docs,
                "embedding_coverage_percent": round((embedded_docs / total_docs * 100) if total_docs > 0 else 0, 1),
                "embedding_model": self.embedding_model_name,
                "embedding_dimensions": self.embedding_dimensions,
                "source_breakdown": source_breakdown,
                "search_config": {
                    "max_results": self.max_results,
                    "similarity_threshold": self.similarity_threshold,
                    "rerank_enabled": self.rerank_results
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return {}


# Global instance
vector_search_service = VectorSearchService()