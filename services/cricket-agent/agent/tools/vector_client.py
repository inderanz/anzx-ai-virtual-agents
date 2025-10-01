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

# Import Matching Engine
try:
    from .vertex_matching_engine import VertexMatchingEngine
    MATCHING_ENGINE_AVAILABLE = True
except ImportError:
    MATCHING_ENGINE_AVAILABLE = False
    logger.warning("Vertex Matching Engine not available")

# Import Redis Storage
try:
    from .redis_storage import RedisStorage
    REDIS_STORAGE_AVAILABLE = True
except ImportError:
    REDIS_STORAGE_AVAILABLE = False
    logger.warning("Redis Storage not available")

# Import Firestore Storage
try:
    from .firestore_storage import FirestoreStorage
    FIRESTORE_STORAGE_AVAILABLE = True
except ImportError:
    FIRESTORE_STORAGE_AVAILABLE = False
    logger.warning("Firestore Storage not available")

# Import Cloud Storage Persistence
try:
    from .cloud_storage_persistence import CloudStoragePersistence
    CLOUD_STORAGE_PERSISTENCE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_PERSISTENCE_AVAILABLE = False
    logger.warning("Cloud Storage Persistence not available")

logger = logging.getLogger(__name__)

class VectorClient:
    """Vertex RAG vector client with metadata filtering and delta upserts"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.embedding_model = "text-embedding-005"
        
        # Initialize shared storage paths
        self.shared_storage_path = "/tmp/cricket-vectors/shared_storage.json"
        self.gcs_bucket = f"{project_id}-cricket-vectors"
        self.gcs_path = "vector_store/shared_storage.json"
        
        # Initialize Cloud Storage persistence for cross-request persistence (primary)
        self.cloud_storage_persistence = None
        if CLOUD_STORAGE_PERSISTENCE_AVAILABLE:
            try:
                self.cloud_storage_persistence = CloudStoragePersistence(project_id=project_id)
                logger.info("Cloud Storage persistence initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Cloud Storage persistence: {e}")
                self.cloud_storage_persistence = None
        
        # Initialize Firestore storage for cross-request persistence (secondary)
        self.firestore_storage = None
        if FIRESTORE_STORAGE_AVAILABLE:
            try:
                self.firestore_storage = FirestoreStorage(project_id=project_id)
                logger.info("Firestore storage initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Firestore storage: {e}")
                self.firestore_storage = None
        
        # Initialize Redis storage for cross-request persistence (fallback)
        self.redis_storage = None
        if REDIS_STORAGE_AVAILABLE:
            try:
                self.redis_storage = RedisStorage(project_id=project_id)
                logger.info("Redis storage initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis storage: {e}")
                self.redis_storage = None
        
        # Initialize local storage
        self._stored_documents = {}
        
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
        
        # Initialize Matching Engine if available
        self.matching_engine = None
        if MATCHING_ENGINE_AVAILABLE:
            try:
                self.matching_engine = VertexMatchingEngine(project_id, location)
                logger.info("Vertex Matching Engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Matching Engine: {e}")
                self.matching_engine = None
        
        # Cache for content hashes to enable delta upserts
        self.content_hashes: Dict[str, str] = {}
        
        # Load from shared storage on initialization (PRIMARY)
        try:
            self._load_from_shared_storage()
            logger.info(f"Loaded {len(self._stored_documents)} documents from shared storage on startup")
        except Exception as e:
            logger.warning(f"Failed to load from shared storage on startup: {e}")
            # Fallback to local storage
            try:
                self._load_from_local_storage()
                logger.info(f"Loaded {len(self._stored_documents)} documents from local storage on startup")
            except Exception as e2:
                logger.warning(f"Failed to load from local storage on startup: {e2}")
                # Try GCS as fallback
                try:
                    self._load_from_gcs()
                    logger.info(f"Loaded {len(self._stored_documents)} documents from GCS on startup")
                except Exception as e3:
                    logger.warning(f"Failed to load from GCS on startup: {e3}")
                    # Continue with empty storage
        
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
            
            # Store documents in a persistent way that can be upgraded to Matching Engine
            # For now, use a combination of local storage and GCS for persistence
            
            # Initialize local storage if not exists
            if not hasattr(self, '_stored_documents'):
                self._stored_documents = {}
            
            # Store documents with their text and metadata
            for i, doc in enumerate(docs):
                if i < len(embeddings):
                    doc_id = doc["id"]
                    self._stored_documents[doc_id] = {
                        "text": doc["text"],
                        "metadata": doc.get("metadata", {}),
                        "embedding": embeddings[i]
                    }
            
            # Store in Matching Engine if available
            if self.matching_engine:
                try:
                    logger.info("Storing documents in Vertex Matching Engine")
                    self.matching_engine.upsert_documents(docs, embeddings)
                    logger.info("Documents stored in Matching Engine")
                except Exception as e:
                    logger.warning(f"Failed to store in Matching Engine: {e}")
            
            # Store in shared storage for persistence across requests
            try:
                self._save_to_shared_storage()
            except Exception as e:
                logger.warning(f"Failed to persist to shared storage: {e}")
            
            # Also store in local storage for backup
            try:
                self._persist_to_local_storage()
            except Exception as e:
                logger.warning(f"Failed to persist to local storage: {e}")
            
            # Also store in GCS for backup
            try:
                self._persist_to_gcs(docs, embeddings)
            except Exception as e:
                logger.warning(f"Failed to persist to GCS: {e}")
            
            logger.info(f"Successfully stored {len(docs)} documents (total: {len(self._stored_documents)})")
            
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
            
            # Implement semantic vector search with fallback to text search
            logger.info(f"Querying vector store with text: '{text[:50]}...', filters: {filters}, k: {k}")
            
            try:
                # CRITICAL FIX: Always load from shared storage first to handle Cloud Run's stateless nature
                try:
                    self._load_from_shared_storage()
                    logger.info(f"Loaded {len(self._stored_documents)} documents from shared storage before query")
                except Exception as e:
                    logger.warning(f"Failed to load from shared storage: {e}")
                
                # Get stored documents from the local cache (now loaded from shared storage)
                stored_docs = getattr(self, '_stored_documents', {})
                
                if not stored_docs:
                    logger.warning("No documents stored in vector store after loading from shared storage")
                    return []
                
                # Try Matching Engine first if available
                if self.matching_engine and self.matching_engine.index_endpoint_id:
                    try:
                        logger.info("Using Vertex Matching Engine for query")
                        matching_results = self.matching_engine.query(query_embedding, k, filters)
                        results = [result["id"] for result in matching_results]
                        logger.info(f"Matching Engine returned {len(results)} results")
                        return results
                    except Exception as e:
                        logger.warning(f"Matching Engine query failed: {e}")
                
                # Fallback to local semantic search
                logger.info("Using local semantic search")
                results = self._semantic_search(text, query_embedding, stored_docs, filters, k)
                
                logger.info(f"Vector store query returned {len(results)} results")
                return results
                
            except Exception as query_error:
                logger.error(f"Vector store query failed: {query_error}")
                return []
            
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
    
    def initialize_matching_engine(self) -> bool:
        """Initialize Vertex AI Matching Engine"""
        try:
            if not self.matching_engine:
                logger.warning("Matching Engine not available")
                return False
            
            # Create index if not exists
            if not self.matching_engine.index_id:
                logger.info("Creating Matching Engine index")
                self.matching_engine.create_index(dimensions=768)
            
            # Create endpoint if not exists
            if not self.matching_engine.index_endpoint_id:
                logger.info("Creating Matching Engine endpoint")
                self.matching_engine.create_index_endpoint()
            
            # Deploy index if not deployed
            if not self.matching_engine.deployed_index_id:
                logger.info("Deploying index to endpoint")
                self.matching_engine.deploy_index(
                    self.matching_engine.index_id,
                    self.matching_engine.index_endpoint_id
                )
            
            logger.info("Matching Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Matching Engine: {e}")
            return False
    
    def get_matching_engine_status(self) -> Dict[str, Any]:
        """Get Matching Engine status"""
        if not self.matching_engine:
            return {"status": "not_available"}
        
        return self.matching_engine.get_index_status()
    
    def clear_corrupted_storage(self) -> None:
        """Clear corrupted storage and reinitialize"""
        try:
            import os
            import shutil
            
            # Clear shared storage
            if os.path.exists(self.shared_storage_path):
                os.remove(self.shared_storage_path)
                logger.info("Cleared corrupted shared storage")
            
            # Clear local storage
            local_storage_path = "/tmp/cricket-vectors/stored_documents.json"
            if os.path.exists(local_storage_path):
                os.remove(local_storage_path)
                logger.info("Cleared corrupted local storage")
            
            # Clear entire directory and recreate
            storage_dir = "/tmp/cricket-vectors"
            if os.path.exists(storage_dir):
                shutil.rmtree(storage_dir)
                logger.info("Cleared corrupted storage directory")
            
            # Reinitialize storage
            os.makedirs(storage_dir, exist_ok=True)
            self._stored_documents = {}
            
            logger.info("Storage cleared and reinitialized")
            
        except Exception as e:
            logger.error(f"Failed to clear corrupted storage: {e}")
            raise
    
    def _persist_to_gcs(self, docs: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Persist documents to GCS for backup"""
        try:
            from google.cloud import storage
            import json
            import time
            
            # Initialize GCS client
            client = storage.Client()
            bucket_name = f"{self.project_id}-cricket-vectors"
            
            logger.info(f"Attempting to persist {len(docs)} documents to GCS bucket: {bucket_name}")
            
            # Create bucket if it doesn't exist
            try:
                bucket = client.bucket(bucket_name)
                if not bucket.exists():
                    logger.info(f"Creating GCS bucket: {bucket_name}")
                    bucket = client.create_bucket(bucket_name, location="us-central1")
                    logger.info(f"GCS bucket created successfully: {bucket_name}")
                else:
                    logger.info(f"GCS bucket already exists: {bucket_name}")
            except Exception as e:
                logger.error(f"GCS bucket creation/access failed: {e}")
                # Try to continue with existing bucket
                try:
                    bucket = client.bucket(bucket_name)
                except Exception as e2:
                    logger.error(f"Failed to access bucket: {e2}")
                    return
            
            # Store documents as JSON
            timestamp = int(time.time())
            success_count = 0
            
            for i, doc in enumerate(docs):
                if i < len(embeddings):
                    try:
                        doc_data = {
                            "id": doc["id"],
                            "text": doc["text"],
                            "metadata": doc.get("metadata", {}),
                            "embedding": embeddings[i],
                            "timestamp": timestamp
                        }
                        
                        blob_name = f"vectors/{doc['id']}.json"
                        blob = bucket.blob(blob_name)
                        blob.upload_from_string(json.dumps(doc_data))
                        success_count += 1
                        logger.debug(f"Persisted document {doc['id']} to GCS")
                    except Exception as e:
                        logger.error(f"Failed to persist document {doc.get('id', 'unknown')}: {e}")
            
            logger.info(f"Successfully persisted {success_count}/{len(docs)} documents to GCS")
            
        except Exception as e:
            logger.error(f"GCS persistence failed: {e}")
            # Don't raise exception, just log the error
            logger.warning("Continuing without GCS persistence")
    
    def _load_from_gcs(self) -> None:
        """Load documents from GCS"""
        try:
            from google.cloud import storage
            import json
            
            # Initialize GCS client
            client = storage.Client()
            bucket_name = f"{self.project_id}-cricket-vectors"
            
            logger.info(f"Attempting to load documents from GCS bucket: {bucket_name}")
            
            try:
                bucket = client.bucket(bucket_name)
                if not bucket.exists():
                    logger.warning(f"GCS bucket {bucket_name} does not exist")
                    return
                else:
                    logger.info(f"GCS bucket {bucket_name} exists")
            except Exception as e:
                logger.error(f"GCS bucket access failed: {e}")
                return
            
            # Load documents
            try:
                blobs = bucket.list_blobs(prefix="vectors/")
                self._stored_documents = {}
                loaded_count = 0
                
                for blob in blobs:
                    if blob.name.endswith('.json'):
                        try:
                            content = blob.download_as_text()
                            doc_data = json.loads(content)
                            
                            doc_id = doc_data.get('id')
                            if doc_id:
                                self._stored_documents[doc_id] = {
                                    "text": doc_data.get('text', ''),
                                    "metadata": doc_data.get('metadata', {}),
                                    "embedding": doc_data.get('embedding', [])
                                }
                                loaded_count += 1
                                logger.debug(f"Loaded document {doc_id} from GCS")
                        except Exception as e:
                            logger.warning(f"Failed to load document {blob.name}: {e}")
                
                logger.info(f"Successfully loaded {loaded_count} documents from GCS")
                
            except Exception as e:
                logger.error(f"Failed to list blobs from GCS: {e}")
                return
            
        except Exception as e:
            logger.error(f"GCS loading failed: {e}")
            # Don't raise exception, just log the error
            logger.warning("Continuing without GCS data")
    
    def _semantic_search(self, text: str, query_embedding: List[float], stored_docs: Dict, filters: Dict[str, Any], k: int) -> List[str]:
        """Perform semantic search using cosine similarity"""
        import numpy as np
        
        if not query_embedding:
            # Fallback to text search
            return self._text_search(text, stored_docs, filters, k)
        
        # Calculate cosine similarity for each document
        similarities = []
        
        for doc_id, doc_data in stored_docs.items():
            doc_embedding = doc_data.get('embedding', [])
            metadata = doc_data.get('metadata', {})
            
            # Apply metadata filters
            if filters:
                matches_filter = True
                for key, value in filters.items():
                    if value and metadata.get(key) != value:
                        matches_filter = False
                        break
                if not matches_filter:
                    continue
            
            if doc_embedding and len(doc_embedding) == len(query_embedding):
                # Calculate cosine similarity
                try:
                    query_vec = np.array(query_embedding)
                    doc_vec = np.array(doc_embedding)
                    
                    # Normalize vectors
                    query_norm = np.linalg.norm(query_vec)
                    doc_norm = np.linalg.norm(doc_vec)
                    
                    if query_norm > 0 and doc_norm > 0:
                        similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
                        similarities.append((doc_id, similarity))
                except Exception as e:
                    logger.warning(f"Similarity calculation failed for {doc_id}: {e}")
                    continue
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [doc_id for doc_id, _ in similarities[:k]]
        
        logger.info(f"Semantic search found {len(results)} results")
        return results
    
    def _text_search(self, text: str, stored_docs: Dict, filters: Dict[str, Any], k: int) -> List[str]:
        """Fallback text-based search"""
        query_lower = text.lower()
        results = []
        
        for doc_id, doc_data in stored_docs.items():
            doc_text = doc_data.get('text', '').lower()
            metadata = doc_data.get('metadata', {})
            
            # Apply metadata filters
            if filters:
                matches_filter = True
                for key, value in filters.items():
                    if value and metadata.get(key) != value:
                        matches_filter = False
                        break
                if not matches_filter:
                    continue
            
            # Check if query matches document content
            if any(word in doc_text for word in query_lower.split()):
                results.append(doc_id)
                if len(results) >= k:
                    break
        
        logger.info(f"Text search found {len(results)} results")
        return results
    
    def _persist_to_local_storage(self) -> None:
        """Persist documents to local storage"""
        try:
            import json
            import os
            
            # Create data directory if it doesn't exist
            data_dir = "/tmp/cricket-vectors"
            os.makedirs(data_dir, exist_ok=True)
            
            # Save documents to local file
            storage_file = os.path.join(data_dir, "stored_documents.json")
            
            with open(storage_file, 'w') as f:
                json.dump(self._stored_documents, f, indent=2)
            
            logger.info(f"Persisted {len(self._stored_documents)} documents to local storage")
            
        except Exception as e:
            logger.error(f"Local storage persistence failed: {e}")
            raise
    
    def _load_from_local_storage(self) -> None:
        """Load documents from local storage"""
        try:
            import json
            import os
            
            # Check if local storage file exists
            data_dir = "/tmp/cricket-vectors"
            storage_file = os.path.join(data_dir, "stored_documents.json")
            
            if not os.path.exists(storage_file):
                logger.info("No local storage file found")
                return
            
            # Load documents from local file
            with open(storage_file, 'r') as f:
                self._stored_documents = json.load(f)
            
            logger.info(f"Loaded {len(self._stored_documents)} documents from local storage")
            
        except Exception as e:
            logger.error(f"Local storage loading failed: {e}")
            raise
    
    def _load_from_shared_storage(self) -> None:
        """Load documents from shared storage (Cloud Storage, Firestore, Redis, or file-based)"""
        try:
            # Try Cloud Storage persistence first (primary)
            if self.cloud_storage_persistence:
                try:
                    self._stored_documents = self.cloud_storage_persistence.load_documents()
                    logger.info(f"Loaded {len(self._stored_documents)} documents from Cloud Storage persistence")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load from Cloud Storage persistence: {e}")
            
            # Try Firestore storage second
            if self.firestore_storage:
                try:
                    self._stored_documents = self.firestore_storage.load_documents()
                    logger.info(f"Loaded {len(self._stored_documents)} documents from Firestore storage")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load from Firestore storage: {e}")
            
            # Try Redis storage third (fallback)
            if self.redis_storage:
                try:
                    self._stored_documents = self.redis_storage.load_documents()
                    logger.info(f"Loaded {len(self._stored_documents)} documents from Redis storage")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load from Redis storage: {e}")
            
            # Fallback to file-based storage
            import json
            import os
            
            # Create shared storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.shared_storage_path), exist_ok=True)
            
            # Try to load from shared storage file
            if os.path.exists(self.shared_storage_path):
                try:
                    with open(self.shared_storage_path, 'r') as f:
                        data = json.load(f)
                        self._stored_documents = data.get('documents', {})
                        logger.info(f"Loaded {len(self._stored_documents)} documents from file storage")
                except json.JSONDecodeError as e:
                    logger.warning(f"Corrupted shared storage file: {e}")
                    # Try to load from GCS as fallback
                    self._load_from_gcs()
                except Exception as e:
                    logger.warning(f"Failed to load from shared storage: {e}")
                    # Try to load from GCS as fallback
                    self._load_from_gcs()
            else:
                # Try to load from GCS as fallback
                self._load_from_gcs()
                
        except Exception as e:
            logger.warning(f"Shared storage loading failed: {e}")
            # Fallback to local storage
            self._load_from_local_storage()
    
    def _save_to_shared_storage(self) -> None:
        """Save documents to shared storage (Cloud Storage, Firestore, Redis, or file-based)"""
        try:
            # Try Cloud Storage persistence first (primary)
            if self.cloud_storage_persistence:
                try:
                    success = self.cloud_storage_persistence.store_documents(self._stored_documents)
                    if success:
                        logger.info(f"Saved {len(self._stored_documents)} documents to Cloud Storage persistence")
                        return
                    else:
                        logger.warning("Failed to save to Cloud Storage persistence, falling back to Firestore")
                except Exception as e:
                    logger.warning(f"Failed to save to Cloud Storage persistence: {e}")
            
            # Try Firestore storage second
            if self.firestore_storage:
                try:
                    success = self.firestore_storage.store_documents(self._stored_documents)
                    if success:
                        logger.info(f"Saved {len(self._stored_documents)} documents to Firestore storage")
                        return
                    else:
                        logger.warning("Failed to save to Firestore storage, falling back to Redis")
                except Exception as e:
                    logger.warning(f"Failed to save to Firestore storage: {e}")
            
            # Try Redis storage third (fallback)
            if self.redis_storage:
                try:
                    success = self.redis_storage.store_documents(self._stored_documents)
                    if success:
                        logger.info(f"Saved {len(self._stored_documents)} documents to Redis storage")
                        return
                    else:
                        logger.warning("Failed to save to Redis storage, falling back to file storage")
                except Exception as e:
                    logger.warning(f"Failed to save to Redis storage: {e}")
            
            # Fallback to file-based storage
            import json
            import os
            
            # Create shared storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.shared_storage_path), exist_ok=True)
            
            # Save to shared storage file
            data = {
                'documents': self._stored_documents,
                'last_updated': datetime.utcnow().isoformat(),
                'total_documents': len(self._stored_documents)
            }
            
            with open(self.shared_storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self._stored_documents)} documents to file storage")
            
            # Also save to GCS as backup
            try:
                self._persist_to_gcs_backup(data)
            except Exception as e:
                logger.warning(f"GCS backup failed: {e}")
                
        except Exception as e:
            logger.error(f"Shared storage saving failed: {e}")
            raise
    
    def _persist_to_gcs_backup(self, data: Dict[str, Any]) -> None:
        """Persist data to GCS as backup"""
        try:
            from google.cloud import storage
            
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_path)
            
            # Upload data to GCS
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"Backed up {len(data.get('documents', {}))} documents to GCS")
            
        except Exception as e:
            logger.warning(f"GCS backup failed: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[str]:
        """Get document content by ID"""
        try:
            # Try Cloud Storage persistence first (primary)
            if self.cloud_storage_persistence:
                try:
                    doc_data = self.cloud_storage_persistence.get_document(doc_id)
                    if doc_data:
                        return doc_data.get('text', '')
                except Exception as e:
                    logger.warning(f"Failed to get document from Cloud Storage persistence: {e}")
            
            # Try Firestore storage second
            if self.firestore_storage:
                try:
                    doc_data = self.firestore_storage.get_document(doc_id)
                    if doc_data:
                        return doc_data.get('text', '')
                except Exception as e:
                    logger.warning(f"Failed to get document from Firestore: {e}")
            
            # Try Redis storage third (fallback)
            if self.redis_storage:
                try:
                    doc_data = self.redis_storage.get_document(doc_id)
                    if doc_data:
                        return doc_data.get('text', '')
                except Exception as e:
                    logger.warning(f"Failed to get document from Redis: {e}")
            
            # Fallback to local cache
            stored_docs = getattr(self, '_stored_documents', {})
            
            if doc_id in stored_docs:
                doc_data = stored_docs[doc_id]
                return doc_data.get('text', '')
            
            # Try to load from shared storage if not in cache
            if not stored_docs:
                try:
                    self._load_from_shared_storage()
                    stored_docs = getattr(self, '_stored_documents', {})
                    if doc_id in stored_docs:
                        doc_data = stored_docs[doc_id]
                        return doc_data.get('text', '')
                except Exception as e:
                    logger.warning(f"Failed to load from shared storage: {e}")
            
            # Try to load from GCS if not in cache
            if not stored_docs:
                try:
                    self._load_from_gcs()
                    stored_docs = getattr(self, '_stored_documents', {})
                    if doc_id in stored_docs:
                        doc_data = stored_docs[doc_id]
                        return doc_data.get('text', '')
                except Exception as e:
                    logger.warning(f"Failed to load from GCS: {e}")
            
            logger.warning(f"Document {doc_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None

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
    """Get vector client instance with Redis-based shared storage"""
    settings = get_settings()
    
    # Use mock client only for test environment
    if settings.app_env == "test":
        logger.info("Using MockVectorClient for test environment")
        return MockVectorClient(
            project_id=settings.gcp_project or "test-project",
            location=settings.vertex_location
        )
    else:
        # Use real Vertex RAG client for production with Redis storage
        logger.info(f"Using VectorClient for production environment (app_env: {settings.app_env})")
        client = VectorClient(
            project_id=settings.gcp_project or "your-project-id",
            location=settings.vertex_location
        )
        
        # Ensure shared storage is loaded
        try:
            client._load_from_shared_storage()
            logger.info(f"Loaded {len(client._stored_documents)} documents from shared storage")
        except Exception as e:
            logger.warning(f"Failed to load from shared storage: {e}")
        
        return client

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
