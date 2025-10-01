"""
Firestore-based persistent storage for Cricket Agent
Free tier alternative to Redis for Cloud Run persistent storage
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logging.warning("Firestore not available")

logger = logging.getLogger(__name__)

class FirestoreStorage:
    """Firestore-based persistent storage for vector documents"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or "virtual-stratum-473511-u5"
        self.db = None
        self.collection_name = "cricket_agent_documents"
        self.metadata_doc_id = "metadata"
        
        # Initialize Firestore connection
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore connection"""
        try:
            if FIRESTORE_AVAILABLE:
                # Initialize Firestore client
                self.db = firestore.Client(project=self.project_id)
                logger.info("Firestore connection established")
            else:
                logger.warning("Firestore not available, using fallback storage")
                self._initialize_fallback_storage()
                
        except Exception as e:
            logger.warning(f"Firestore connection failed: {e}, using fallback storage")
            self._initialize_fallback_storage()
    
    def _initialize_fallback_storage(self):
        """Initialize fallback file-based storage"""
        try:
            import os
            import json
            
            # Create fallback storage directory
            self.fallback_dir = "/tmp/cricket-vectors-firestore-fallback"
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
        """Store documents in Firestore"""
        try:
            if self.db:
                # Store in Firestore
                batch = self.db.batch()
                
                for doc_id, doc_data in documents.items():
                    doc_ref = self.db.collection(self.collection_name).document(doc_id)
                    batch.set(doc_ref, {
                        "id": doc_id,
                        "text": doc_data.get("text", ""),
                        "metadata": doc_data.get("metadata", {}),
                        "embedding": doc_data.get("embedding", []),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                
                # Update metadata
                metadata_ref = self.db.collection(self.collection_name).document(self.metadata_doc_id)
                batch.set(metadata_ref, {
                    "total_documents": len(documents),
                    "last_updated": datetime.utcnow(),
                    "storage_type": "firestore"
                })
                
                # Commit batch
                batch.commit()
                logger.info(f"Stored {len(documents)} documents in Firestore")
                
            else:
                # Store in fallback storage
                self.fallback_data["documents"].update(documents)
                self.fallback_data["metadata"] = {
                    "total_documents": len(self.fallback_data["documents"]),
                    "last_updated": datetime.utcnow().isoformat(),
                    "storage_type": "fallback"
                }
                
                # Save to file
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
                
                logger.info(f"Stored {len(documents)} documents in fallback storage")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store documents: {e}")
            return False
    
    def load_documents(self) -> Dict[str, Any]:
        """Load documents from Firestore"""
        try:
            if self.db:
                # Load from Firestore
                docs = self.db.collection(self.collection_name).stream()
                documents = {}
                
                for doc in docs:
                    if doc.id != self.metadata_doc_id:
                        doc_data = doc.to_dict()
                        documents[doc.id] = {
                            "text": doc_data.get("text", ""),
                            "metadata": doc_data.get("metadata", {}),
                            "embedding": doc_data.get("embedding", [])
                        }
                
                logger.info(f"Loaded {len(documents)} documents from Firestore")
                return documents
                
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
            if self.db:
                # Get from Firestore
                doc_ref = self.db.collection(self.collection_name).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    doc_data = doc.to_dict()
                    return {
                        "text": doc_data.get("text", ""),
                        "metadata": doc_data.get("metadata", {}),
                        "embedding": doc_data.get("embedding", [])
                    }
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
            if self.db:
                # Delete from Firestore
                doc_ref = self.db.collection(self.collection_name).document(doc_id)
                doc_ref.delete()
                return True
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
            if self.db:
                # Get from Firestore
                metadata_ref = self.db.collection(self.collection_name).document(self.metadata_doc_id)
                metadata_doc = metadata_ref.get()
                
                if metadata_doc.exists:
                    data = metadata_doc.to_dict()
                    return {
                        "storage_type": "firestore",
                        "total_documents": data.get("total_documents", 0),
                        "last_updated": data.get("last_updated").isoformat() if data.get("last_updated") else None,
                        "firestore_connected": True
                    }
                else:
                    return {
                        "storage_type": "firestore",
                        "total_documents": 0,
                        "last_updated": None,
                        "firestore_connected": True
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
                            "firestore_connected": False
                        }
                else:
                    return {
                        "storage_type": "none",
                        "total_documents": 0,
                        "last_updated": None,
                        "firestore_connected": False
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return {"error": str(e)}
    
    def clear_all(self) -> bool:
        """Clear all documents"""
        try:
            if self.db:
                # Clear Firestore
                docs = self.db.collection(self.collection_name).stream()
                batch = self.db.batch()
                
                for doc in docs:
                    batch.delete(doc.reference)
                
                batch.commit()
                logger.info("Cleared all documents from Firestore")
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
            if self.db:
                # Test Firestore connection
                self.db.collection(self.collection_name).limit(1).get()
                return {
                    "status": "healthy",
                    "storage_type": "firestore",
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
