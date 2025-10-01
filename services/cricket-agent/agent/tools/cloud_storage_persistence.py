"""
Cloud Storage-based persistent storage for Cricket Agent
Reliable file-based persistence using Google Cloud Storage
"""

import json
import logging
import os
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from google.cloud import storage
    CLOUD_STORAGE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_AVAILABLE = False
    logging.warning("Cloud Storage not available")

logger = logging.getLogger(__name__)

class CloudStoragePersistence:
    """Cloud Storage-based persistent storage for vector documents"""
    
    def __init__(self, project_id: str = None, bucket_name: str = None):
        self.project_id = project_id or "virtual-stratum-473511-u5"
        self.bucket_name = bucket_name or f"{self.project_id}-cricket-persistent-storage"
        self.storage_client = None
        self.bucket = None
        
        # Initialize Cloud Storage connection
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Cloud Storage connection"""
        try:
            if CLOUD_STORAGE_AVAILABLE:
                # Initialize Cloud Storage client
                self.storage_client = storage.Client(project=self.project_id)
                self.bucket = self.storage_client.bucket(self.bucket_name)
                
                # CRITICAL: Verify bucket exists
                if not self.bucket.exists():
                    logger.error(f"Bucket {self.bucket_name} does not exist!")
                    raise Exception(f"Bucket {self.bucket_name} not found")
                
                logger.info(f"Cloud Storage connection established to bucket: {self.bucket_name}")
            else:
                logger.error("Cloud Storage library not available - CRITICAL ERROR")
                raise Exception("Cloud Storage not available")
                
        except Exception as e:
            logger.error(f"Cloud Storage connection FAILED: {e}")
            logger.error("Using fallback storage - DATA WILL NOT PERSIST!")
            self._initialize_fallback_storage()
    
    def _initialize_fallback_storage(self):
        """Initialize fallback file-based storage"""
        try:
            import os
            import json
            
            # Create fallback storage directory
            self.fallback_dir = "/tmp/cricket-vectors-storage-fallback"
            os.makedirs(self.fallback_dir, exist_ok=True)
            
            self.fallback_file = os.path.join(self.fallback_dir, "storage.json")
            
            # Load existing data
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
    
    def store_documents(self, documents: Dict[str, Any]) -> bool:
        """Store documents in Cloud Storage"""
        try:
            logger.info(f"store_documents called with {len(documents)} documents")
            logger.info(f"self.bucket is None: {self.bucket is None}")
            logger.info(f"self.bucket_name: {self.bucket_name}")
            
            if self.bucket:
                # Store in Cloud Storage
                logger.info(f"Attempting to store to Cloud Storage bucket: {self.bucket_name}")
                blob = self.bucket.blob("vector_store/documents.json")
                
                # Prepare data
                data = {
                    "documents": documents,
                    "metadata": {
                        "total_documents": len(documents),
                        "last_updated": datetime.utcnow().isoformat(),
                        "storage_type": "cloud_storage"
                    }
                }
                
                # Upload to Cloud Storage
                blob.upload_from_string(
                    json.dumps(data, indent=2),
                    content_type='application/json'
                )
                
                logger.info(f"✅ Successfully stored {len(documents)} documents in Cloud Storage!")
                
            else:
                # Store in fallback storage
                logger.warning(f"⚠️ Using fallback storage - self.bucket is None!")
                self.fallback_data["documents"].update(documents)
                self.fallback_data["metadata"] = {
                    "total_documents": len(self.fallback_data["documents"]),
                    "last_updated": datetime.utcnow().isoformat(),
                    "storage_type": "fallback"
                }
                
                # Save to file
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
                
                logger.warning(f"⚠️ Stored {len(documents)} documents in FALLBACK storage (NOT PERSISTENT!)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store documents: {e}")
            return False
    
    def load_documents(self) -> Dict[str, Any]:
        """Load documents from Cloud Storage"""
        try:
            if self.bucket:
                # Load from Cloud Storage
                blob = self.bucket.blob("vector_store/documents.json")
                
                if blob.exists():
                    data = json.loads(blob.download_as_text())
                    documents = data.get("documents", {})
                    logger.info(f"Loaded {len(documents)} documents from Cloud Storage")
                    return documents
                else:
                    logger.info("No documents found in Cloud Storage")
                    return {}
                    
            else:
                # Load from fallback storage
                if os.path.exists(self.fallback_file):
                    with open(self.fallback_file, 'r') as f:
                        data = json.load(f)
                        documents = data.get("documents", {})
                        logger.info(f"Loaded {len(documents)} documents from fallback storage")
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
            documents = self.load_documents()
            return documents.get(doc_id)
                
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete specific document"""
        try:
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
            if self.bucket:
                # Get from Cloud Storage
                blob = self.bucket.blob("vector_store/documents.json")
                
                if blob.exists():
                    data = json.loads(blob.download_as_text())
                    return {
                        "storage_type": "cloud_storage",
                        "total_documents": len(data.get("documents", {})),
                        "last_updated": data.get("metadata", {}).get("last_updated"),
                        "cloud_storage_connected": True
                    }
                else:
                    return {
                        "storage_type": "cloud_storage",
                        "total_documents": 0,
                        "last_updated": None,
                        "cloud_storage_connected": True
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
                            "cloud_storage_connected": False
                        }
                else:
                    return {
                        "storage_type": "none",
                        "total_documents": 0,
                        "last_updated": None,
                        "cloud_storage_connected": False
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return {"error": str(e)}
    
    def clear_all(self) -> bool:
        """Clear all documents"""
        try:
            if self.bucket:
                # Clear Cloud Storage
                blob = self.bucket.blob("vector_store/documents.json")
                if blob.exists():
                    blob.delete()
                logger.info("Cleared all documents from Cloud Storage")
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
            if self.bucket:
                # Test Cloud Storage connection
                self.bucket.blob("health_check").upload_from_string("test")
                self.bucket.blob("health_check").delete()
                return {
                    "status": "healthy",
                    "storage_type": "cloud_storage",
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
