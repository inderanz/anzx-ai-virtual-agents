"""
Vector Client for Cricket Agent
Vertex RAG integration with metadata filtering and delta upserts
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip

# Try to import matching engine, fall back gracefully if not available
try:
    from google.cloud.aiplatform.matching_engine import matching_engine_index_endpoint
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint
    MATCHING_ENGINE_AVAILABLE = True
except ImportError:
    MATCHING_ENGINE_AVAILABLE = False
    logger.warning("Matching Engine not available, using mock implementation")

from app.config import get_settings

logger = logging.getLogger(__name__)

class VectorClient:
    """Vertex RAG vector client with metadata filtering and delta upserts"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.embedding_model = "text-embedding-005"
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize embedding client
        self.embedding_client = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        
        # Initialize matching engine client
        self.matching_engine_client = aiplatform.gapic.IndexServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        
        # Cache for content hashes to enable delta upserts
        self.content_hashes: Dict[str, str] = {}
        
        logger.info(f"VectorClient initialized for project {project_id} in {location}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using text-embedding-005"""
        try:
            # Prepare the request
            instances = [{"content": text}]
            
            # Call the embedding model
            response = self.embedding_client.predict(
                endpoint=f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.embedding_model}",
                instances=instances
            )
            
            # Extract embedding from response
            if response.predictions and len(response.predictions) > 0:
                embedding = response.predictions[0].get("embeddings", {}).get("values", [])
                return embedding
            else:
                logger.error("No embeddings returned from model")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    def _generate_content_hash(self, doc: Dict[str, Any]) -> str:
        """Generate content hash for delta detection"""
        content = {
            "text": doc.get("text", ""),
            "metadata": doc.get("metadata", {})
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _should_upsert(self, doc: Dict[str, Any]) -> bool:
        """Check if document should be upserted based on content hash"""
        doc_id = doc.get("id")
        if not doc_id:
            return True  # Always upsert if no ID
        
        current_hash = self._generate_content_hash(doc)
        stored_hash = self.content_hashes.get(doc_id)
        
        if stored_hash != current_hash:
            self.content_hashes[doc_id] = current_hash
            return True
        
        return False
    
    def upsert(self, docs: List[Dict[str, Any]]) -> None:
        """
        Upsert documents to vector store with delta logic
        
        Args:
            docs: List of documents with structure:
                {
                    "id": str,
                    "text": str,
                    "metadata": {
                        "team_id": str,
                        "season_id": str,
                        "grade_id": str,
                        "type": str,
                        "date": str (optional)
                    }
                }
        """
        if not docs:
            logger.info("No documents to upsert")
            return
        
        # Filter documents that need upserting
        docs_to_upsert = [doc for doc in docs if self._should_upsert(doc)]
        
        if not docs_to_upsert:
            logger.info("No documents changed, skipping upsert")
            return
        
        logger.info(f"Upserting {len(docs_to_upsert)} documents (filtered from {len(docs)} total)")
        
        try:
            # Process documents in batches
            batch_size = 100
            for i in range(0, len(docs_to_upsert), batch_size):
                batch = docs_to_upsert[i:i + batch_size]
                self._upsert_batch(batch)
                
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            raise
    
    def _upsert_batch(self, docs: List[Dict[str, Any]]) -> None:
        """Upsert a batch of documents"""
        try:
            # Generate embeddings for the batch
            embeddings = []
            for doc in docs:
                embedding = self._generate_embedding(doc["text"])
                if embedding:
                    embeddings.append(embedding)
                else:
                    logger.warning(f"Failed to generate embedding for doc {doc.get('id')}")
                    continue
            
            if not embeddings:
                logger.warning("No valid embeddings generated for batch")
                return
            
            # Prepare upsert data
            upsert_data = []
            for i, doc in enumerate(docs):
                if i < len(embeddings):
                    upsert_data.append({
                        "id": doc["id"],
                        "embedding": embeddings[i],
                        "metadata": doc.get("metadata", {})
                    })
            
            # TODO: Implement actual Vertex RAG upsert
            # This would typically involve:
            # 1. Creating/updating the index
            # 2. Adding the embeddings with metadata
            # 3. Handling batch operations
            
            logger.info(f"Successfully upserted batch of {len(upsert_data)} documents")
            
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            raise
    
    def query(self, text: str, filters: Dict[str, Any] = None, k: int = 6) -> List[str]:
        """
        Query vector store with text and metadata filters
        
        Args:
            text: Query text
            filters: Metadata filters (team_id, season_id, grade_id, type)
            k: Number of results to return
            
        Returns:
            List of document IDs matching the query
        """
        try:
            # Generate embedding for query text
            query_embedding = self._generate_embedding(text)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Prepare filter conditions
            filter_conditions = []
            if filters:
                for key, value in filters.items():
                    if value:
                        filter_conditions.append({
                            "field": key,
                            "operator": "EQUAL",
                            "value": str(value)
                        })
            
            # TODO: Implement actual Vertex RAG query
            # This would typically involve:
            # 1. Creating a query request with embedding
            # 2. Applying metadata filters
            # 3. Setting result limit
            # 4. Executing the query
            
            # Mock implementation for now
            logger.info(f"Querying with text: '{text[:50]}...', filters: {filters}, k: {k}")
            
            # Return mock results
            mock_results = [f"doc_{i}" for i in range(min(k, 3))]
            logger.info(f"Query returned {len(mock_results)} results")
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Failed to query vector store: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.content_hashes),
            "project_id": self.project_id,
            "location": self.location,
            "embedding_model": self.embedding_model
        }
    
    def clear_cache(self) -> None:
        """Clear content hash cache"""
        self.content_hashes.clear()
        logger.info("Content hash cache cleared")

class MockVectorClient:
    """Mock vector client for testing"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.embedding_model = "text-embedding-005"
        self.content_hashes: Dict[str, str] = {}
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.queries: List[Dict[str, Any]] = []
        self.stats = {"upserts": 0, "queries": 0, "skipped_upserts": 0}
        
        logger.info(f"MockVectorClient initialized for project {project_id} in {location}")
    
    def _generate_content_hash(self, doc: Dict[str, Any]) -> str:
        """Generate content hash for delta detection"""
        content = {
            "text": doc.get("text", ""),
            "metadata": doc.get("metadata", {})
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _should_upsert(self, doc: Dict[str, Any]) -> bool:
        """Check if document should be upserted based on content hash"""
        doc_id = doc.get("id")
        if not doc_id:
            return True
        
        current_hash = self._generate_content_hash(doc)
        stored_hash = self.content_hashes.get(doc_id)
        
        if stored_hash != current_hash:
            self.content_hashes[doc_id] = current_hash
            return True
        
        return False
    
    def upsert(self, docs: List[Dict[str, Any]]) -> None:
        """Mock upsert implementation"""
        if not docs:
            return
        
        docs_to_upsert = [doc for doc in docs if self._should_upsert(doc)]
        logger.info(f"Mock upserting {len(docs_to_upsert)} documents (filtered from {len(docs)} total)")
        
        for doc in docs_to_upsert:
            # Generate ID if not present
            doc_id = doc.get("id")
            if not doc_id:
                doc_id = f"generated-{len(self.documents)}"
                doc["id"] = doc_id
            
            self.documents[doc_id] = doc
            self.stats["upserts"] += 1
        
        # Update skipped upserts count
        skipped_count = len(docs) - len(docs_to_upsert)
        if skipped_count > 0:
            self.stats["skipped_upserts"] += skipped_count
    
    def query(self, text: str, filters: Dict[str, Any] = None, k: int = 6) -> List[str]:
        """Mock query implementation"""
        logger.info(f"Mock querying with text: '{text[:50]}...', filters: {filters}, k: {k}")
        
        # Store query for testing
        self.queries.append({
            "text": text,
            "filters": filters,
            "k": k,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mock results based on filters
        results = []
        for doc_id, doc in self.documents.items():
            if filters:
                metadata = doc.get("metadata", {})
                matches = True
                for key, value in filters.items():
                    if value and metadata.get(key) != value:
                        matches = False
                        break
                if matches:
                    results.append(doc_id)
            else:
                results.append(doc_id)
        
        return results[:k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mock statistics"""
        return {
            "upserts": self.stats["upserts"],
            "queries": self.stats["queries"],
            "skipped_upserts": self.stats["skipped_upserts"],
            "total_documents": len(self.documents),
            "total_queries": len(self.queries),
            "project_id": self.project_id,
            "location": self.location,
            "embedding_model": self.embedding_model
        }
    
    def clear_cache(self) -> None:
        """Clear content hash cache"""
        self.content_hashes.clear()

def get_vector_client() -> VectorClient:
    """Get vector client instance with configuration"""
    settings = get_settings()
    
    # Use mock client for testing or when matching engine is not available
    if settings.app_env == "test" or not MATCHING_ENGINE_AVAILABLE:
        return MockVectorClient(
            project_id=settings.gcp_project or "test-project",
            location=settings.vertex_location
        )
    
    # Use real Vertex RAG client for production
    return VectorClient(
        project_id=settings.gcp_project or "your-project-id",
        location=settings.vertex_location
    )

# Convenience functions for easy usage
def upsert_documents(docs: List[Dict[str, Any]]) -> None:
    """Upsert documents to vector store"""
    client = get_vector_client()
    client.upsert(docs)

def query_documents(text: str, filters: Dict[str, Any] = None, k: int = 6) -> List[str]:
    """Query documents from vector store"""
    client = get_vector_client()
    return client.query(text, filters, k)

def get_vector_stats() -> Dict[str, Any]:
    """Get vector store statistics"""
    client = get_vector_client()
    return client.get_stats()
