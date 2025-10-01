"""
Redis-based shared storage for Cricket Agent
Replaces singleton pattern with persistent shared storage
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, falling back to file-based storage")

logger = logging.getLogger(__name__)

class RedisStorage:
    """Redis-based shared storage for vector documents"""
    
    def __init__(self, redis_url: str = None, project_id: str = None):
        self.project_id = project_id or "virtual-stratum-473511-u5"
        self.redis_url = redis_url or "redis://localhost:6379"
        self.redis_client = None
        self.fallback_storage = None
        
        # Cloud Storage bucket for persistent storage
        self.gcs_bucket = f"{self.project_id}-cricket-persistent-storage"
        self.gcs_path = "redis_fallback/storage.json"
        
        # Initialize Redis connection
        self._initialize_redis()
        
        # Storage keys
        self.documents_key = f"cricket_agent:documents:{self.project_id}"
        self.metadata_key = f"cricket_agent:metadata:{self.project_id}"
        self.lock_key = f"cricket_agent:lock:{self.project_id}"
        
    def _initialize_redis(self):
        """Initialize Redis connection with fallback"""
        try:
            if REDIS_AVAILABLE:
                # Try to connect to Redis
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
                
            else:
                logger.warning("Redis not available, using fallback storage")
                self._initialize_fallback_storage()
                
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using fallback storage")
            self._initialize_fallback_storage()
    
    def _initialize_fallback_storage(self):
        """Initialize fallback Cloud Storage-based storage"""
        try:
            import os
            import json
            
            # Create fallback storage directory
            self.fallback_dir = "/tmp/cricket-vectors-redis-fallback"
            os.makedirs(self.fallback_dir, exist_ok=True)
            
            self.fallback_file = os.path.join(self.fallback_dir, "shared_storage.json")
            
            # Try to load from Cloud Storage first
            try:
                self._load_from_gcs()
                logger.info("Loaded data from Cloud Storage")
            except Exception as e:
                logger.warning(f"Failed to load from Cloud Storage: {e}")
                # Load from local file if exists
                if os.path.exists(self.fallback_file):
                    with open(self.fallback_file, 'r') as f:
                        self.fallback_data = json.load(f)
                else:
                    self.fallback_data = {
                        "documents": {},
                        "metadata": {},
                        "last_updated": None
                    }
            
            logger.info("Fallback storage initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize fallback storage: {e}")
            self.fallback_data = {"documents": {}, "metadata": {}}
    
    def _load_from_gcs(self):
        """Load data from Cloud Storage"""
        try:
            from google.cloud import storage
            
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_path)
            
            if blob.exists():
                data = json.loads(blob.download_as_text())
                self.fallback_data = data
                logger.info(f"Loaded {len(data.get('documents', {}))} documents from Cloud Storage")
            else:
                logger.info("No data found in Cloud Storage")
                
        except Exception as e:
            logger.warning(f"Failed to load from Cloud Storage: {e}")
            raise
    
    def _save_to_gcs(self):
        """Save data to Cloud Storage"""
        try:
            from google.cloud import storage
            
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_path)
            
            # Upload data to Cloud Storage
            blob.upload_from_string(
                json.dumps(self.fallback_data, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"Saved {len(self.fallback_data.get('documents', {}))} documents to Cloud Storage")
            
        except Exception as e:
            logger.warning(f"Failed to save to Cloud Storage: {e}")
            raise
    
    def _acquire_lock(self, timeout: int = 10) -> bool:
        """Acquire distributed lock"""
        try:
            if self.redis_client:
                # Use Redis for distributed locking
                lock_value = str(time.time())
                result = self.redis_client.set(
                    self.lock_key,
                    lock_value,
                    nx=True,
                    ex=timeout
                )
                return result is not None
            else:
                # Use file-based locking for fallback
                lock_file = f"{self.fallback_dir}/.lock"
                if os.path.exists(lock_file):
                    # Check if lock is expired
                    if time.time() - os.path.getmtime(lock_file) > timeout:
                        os.remove(lock_file)
                        return True
                    return False
                else:
                    with open(lock_file, 'w') as f:
                        f.write(str(time.time()))
                    return True
        except Exception as e:
            logger.warning(f"Failed to acquire lock: {e}")
            return True  # Continue without lock
    
    def _release_lock(self):
        """Release distributed lock"""
        try:
            if self.redis_client:
                self.redis_client.delete(self.lock_key)
            else:
                lock_file = f"{self.fallback_dir}/.lock"
                if os.path.exists(lock_file):
                    os.remove(lock_file)
        except Exception as e:
            logger.warning(f"Failed to release lock: {e}")
    
    def store_documents(self, documents: Dict[str, Any]) -> bool:
        """Store documents in shared storage"""
        try:
            if not self._acquire_lock():
                logger.warning("Failed to acquire lock, skipping store")
                return False
            
            try:
                if self.redis_client:
                    # Store in Redis
                    self.redis_client.hset(
                        self.documents_key,
                        mapping={doc_id: json.dumps(doc_data) for doc_id, doc_data in documents.items()}
                    )
                    
                    # Update metadata
                    metadata = {
                        "total_documents": len(documents),
                        "last_updated": datetime.utcnow().isoformat(),
                        "storage_type": "redis"
                    }
                    self.redis_client.hset(self.metadata_key, mapping=metadata)
                    
                    logger.info(f"Stored {len(documents)} documents in Redis")
                    
                else:
                    # Store in fallback storage
                    self.fallback_data["documents"].update(documents)
                    self.fallback_data["metadata"] = {
                        "total_documents": len(self.fallback_data["documents"]),
                        "last_updated": datetime.utcnow().isoformat(),
                        "storage_type": "fallback"
                    }
                    
                    # Save to Cloud Storage
                    try:
                        self._save_to_gcs()
                        logger.info(f"Stored {len(documents)} documents in Cloud Storage")
                    except Exception as e:
                        logger.warning(f"Failed to save to Cloud Storage: {e}")
                        # Fallback to local file
                        with open(self.fallback_file, 'w') as f:
                            json.dump(self.fallback_data, f, indent=2)
                        logger.info(f"Stored {len(documents)} documents in local fallback storage")
                
                return True
                
            finally:
                self._release_lock()
                
        except Exception as e:
            logger.error(f"Failed to store documents: {e}")
            return False
    
    def load_documents(self) -> Dict[str, Any]:
        """Load documents from shared storage"""
        try:
            if self.redis_client:
                # Load from Redis
                documents_data = self.redis_client.hgetall(self.documents_key)
                documents = {}
                
                for doc_id, doc_json in documents_data.items():
                    try:
                        documents[doc_id] = json.loads(doc_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse document {doc_id}")
                        continue
                
                logger.info(f"Loaded {len(documents)} documents from Redis")
                return documents
                
            else:
                # Load from fallback storage
                try:
                    # Try Cloud Storage first
                    self._load_from_gcs()
                    documents = self.fallback_data.get("documents", {})
                    logger.info(f"Loaded {len(documents)} documents from Cloud Storage")
                    return documents
                except Exception as e:
                    logger.warning(f"Failed to load from Cloud Storage: {e}")
                    # Fallback to local file
                    if os.path.exists(self.fallback_file):
                        with open(self.fallback_file, 'r') as f:
                            data = json.load(f)
                            documents = data.get("documents", {})
                            logger.info(f"Loaded {len(documents)} documents from local fallback storage")
                            return documents
                    else:
                        logger.info("No fallback storage file found")
                        return {}
                    
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return {}
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get specific document by ID"""
        try:
            if self.redis_client:
                # Get from Redis
                doc_json = self.redis_client.hget(self.documents_key, doc_id)
                if doc_json:
                    return json.loads(doc_json)
                return None
            else:
                # Get from fallback storage
                documents = self.load_documents()
                return documents.get(doc_id)
                
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete specific document"""
        try:
            if self.redis_client:
                # Delete from Redis
                result = self.redis_client.hdel(self.documents_key, doc_id)
                return result > 0
            else:
                # Delete from fallback storage
                documents = self.load_documents()
                if doc_id in documents:
                    del documents[doc_id]
                    return self.store_documents(documents)
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get storage metadata"""
        try:
            if self.redis_client:
                # Get from Redis
                metadata = self.redis_client.hgetall(self.metadata_key)
                return {
                    "storage_type": "redis",
                    "total_documents": int(metadata.get("total_documents", 0)),
                    "last_updated": metadata.get("last_updated"),
                    "redis_connected": True
                }
            else:
                # Get from fallback storage
                if os.path.exists(self.fallback_file):
                    with open(self.fallback_file, 'r') as f:
                        data = json.load(f)
                        return {
                            "storage_type": "fallback",
                            "total_documents": len(data.get("documents", {})),
                            "last_updated": data.get("metadata", {}).get("last_updated"),
                            "redis_connected": False
                        }
                else:
                    return {
                        "storage_type": "none",
                        "total_documents": 0,
                        "last_updated": None,
                        "redis_connected": False
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return {"error": str(e)}
    
    def clear_all(self) -> bool:
        """Clear all documents"""
        try:
            if self.redis_client:
                # Clear Redis
                self.redis_client.delete(self.documents_key)
                self.redis_client.delete(self.metadata_key)
                logger.info("Cleared all documents from Redis")
            else:
                # Clear fallback storage
                self.fallback_data = {"documents": {}, "metadata": {}}
                if os.path.exists(self.fallback_file):
                    with open(self.fallback_file, 'w') as f:
                        json.dump(self.fallback_data, f, indent=2)
                logger.info("Cleared all documents from fallback storage")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear all documents: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check storage health"""
        try:
            if self.redis_client:
                # Test Redis connection
                self.redis_client.ping()
                return {
                    "status": "healthy",
                    "storage_type": "redis",
                    "connected": True
                }
            else:
                # Test fallback storage
                if os.path.exists(self.fallback_file):
                    return {
                        "status": "healthy",
                        "storage_type": "fallback",
                        "connected": True
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "storage_type": "none",
                        "connected": False
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
