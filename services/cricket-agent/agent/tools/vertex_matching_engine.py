"""
Vertex AI Matching Engine Implementation
Production-grade vector database using Google Cloud Vertex AI
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from google.cloud.aiplatform.matching_engine import matching_engine_index_endpoint
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint

logger = logging.getLogger(__name__)

class VertexMatchingEngine:
    """Vertex AI Matching Engine for production vector database"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize clients
        self.index_client = aiplatform.gapic.IndexServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        self.index_endpoint_client = aiplatform.gapic.IndexEndpointServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        
        # Configuration
        self.index_display_name = "cricket-agent-vector-index"
        self.index_endpoint_display_name = "cricket-agent-vector-endpoint"
        self.machine_type = "e2-standard-2"
        self.min_replica_count = 1
        self.max_replica_count = 3
        
        # Storage paths
        self.gcs_bucket = f"{project_id}-cricket-vectors"
        self.embeddings_path = "matching_engine/embeddings.json"
        self.metadata_path = "matching_engine/metadata.json"
        
        # Initialize index and endpoint
        self.index_id = None
        self.index_endpoint_id = None
        self.deployed_index_id = None
        
    def create_index(self, dimensions: int = 768) -> str:
        """Create Vertex AI Matching Engine index"""
        try:
            logger.info(f"Creating Matching Engine index with {dimensions} dimensions")
            
            # Define index metadata
            index_metadata = {
                "contentsDeltaUri": f"gs://{self.gcs_bucket}/{self.embeddings_path}",
                "isCompleteOverwrite": True,
                "dimensions": dimensions,
                "approximateNeighborsCount": 150,
                "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
                "algorithmConfig": {
                    "treeAhConfig": {
                        "leafNodeEmbeddingCount": 500,
                        "leafNodesToSearchPercent": 7
                    }
                }
            }
            
            # Create index
            index = self.index_client.create_index(
                parent=f"projects/{self.project_id}/locations/{self.location}",
                index=aip.Index(
                    display_name=self.index_display_name,
                    description="Cricket Agent Vector Index for RAG",
                    metadata=index_metadata,
                    index_update_method=aip.Index.IndexUpdateMethod.BATCH_UPDATE
                )
            )
            
            # Wait for index creation
            operation = index.operation
            logger.info(f"Index creation operation: {operation.name}")
            
            # Poll for completion
            while not operation.done():
                time.sleep(30)
                operation = self.index_client.get_operation(operation.name)
                logger.info(f"Index creation status: {operation.metadata}")
            
            if operation.error:
                raise Exception(f"Index creation failed: {operation.error}")
            
            # Get the created index
            index_name = operation.response.name
            self.index_id = index_name.split('/')[-1]
            
            logger.info(f"Index created successfully: {self.index_id}")
            return self.index_id
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def create_index_endpoint(self) -> str:
        """Create Vertex AI Matching Engine index endpoint"""
        try:
            logger.info("Creating Matching Engine index endpoint")
            
            # Create index endpoint
            index_endpoint = self.index_endpoint_client.create_index_endpoint(
                parent=f"projects/{self.project_id}/locations/{self.location}",
                index_endpoint=aip.IndexEndpoint(
                    display_name=self.index_endpoint_display_name,
                    description="Cricket Agent Vector Endpoint for RAG"
                )
            )
            
            # Wait for endpoint creation
            operation = index_endpoint.operation
            logger.info(f"Index endpoint creation operation: {operation.name}")
            
            # Poll for completion
            while not operation.done():
                time.sleep(30)
                operation = self.index_endpoint_client.get_operation(operation.name)
                logger.info(f"Index endpoint creation status: {operation.metadata}")
            
            if operation.error:
                raise Exception(f"Index endpoint creation failed: {operation.error}")
            
            # Get the created endpoint
            endpoint_name = operation.response.name
            self.index_endpoint_id = endpoint_name.split('/')[-1]
            
            logger.info(f"Index endpoint created successfully: {self.index_endpoint_id}")
            return self.index_endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create index endpoint: {e}")
            raise
    
    def deploy_index(self, index_id: str, index_endpoint_id: str) -> str:
        """Deploy index to endpoint"""
        try:
            logger.info(f"Deploying index {index_id} to endpoint {index_endpoint_id}")
            
            # Deploy index
            deployed_index = self.index_endpoint_client.deploy_index(
                index_endpoint=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{index_endpoint_id}",
                deployed_index=aip.DeployedIndex(
                    id=f"cricket-agent-deployed-index-{int(time.time())}",
                    index=index_id,
                    display_name="Cricket Agent Deployed Index",
                    enable_access_logging=True,
                    dedicated_resources=aip.DedicatedResources(
                        machine_spec=aip.MachineSpec(
                            machine_type=self.machine_type
                        ),
                        min_replica_count=self.min_replica_count,
                        max_replica_count=self.max_replica_count
                    )
                )
            )
            
            # Wait for deployment
            operation = deployed_index.operation
            logger.info(f"Index deployment operation: {operation.name}")
            
            # Poll for completion
            while not operation.done():
                time.sleep(30)
                operation = self.index_endpoint_client.get_operation(operation.name)
                logger.info(f"Index deployment status: {operation.metadata}")
            
            if operation.error:
                raise Exception(f"Index deployment failed: {operation.error}")
            
            # Get the deployed index
            deployed_index_name = operation.response.name
            self.deployed_index_id = deployed_index_name.split('/')[-1]
            
            logger.info(f"Index deployed successfully: {self.deployed_index_id}")
            return self.deployed_index_id
            
        except Exception as e:
            logger.error(f"Failed to deploy index: {e}")
            raise
    
    def upsert_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Upsert documents to Matching Engine"""
        try:
            logger.info(f"Upserting {len(documents)} documents to Matching Engine")
            
            # Prepare embeddings data
            embeddings_data = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                embeddings_data.append({
                    "id": doc["id"],
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                })
            
            # Save embeddings to GCS
            self._save_embeddings_to_gcs(embeddings_data)
            
            # Update index with new data
            if self.index_id:
                self._update_index_contents()
            
            logger.info(f"Successfully upserted {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            raise
    
    def query(self, query_embedding: List[float], k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query Matching Engine for similar documents"""
        try:
            if not self.index_endpoint_id or not self.deployed_index_id:
                logger.warning("Index endpoint not deployed, falling back to local search")
                return []
            
            # Create query request
            query_request = aip.QueryRequest(
                deployed_index_id=self.deployed_index_id,
                queries=[aip.Query(
                    embedding=query_embedding,
                    top_k=k,
                    filter=filter
                )]
            )
            
            # Execute query
            response = self.index_endpoint_client.query_index_endpoint(
                index_endpoint=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_endpoint_id}",
                deployed_index_id=self.deployed_index_id,
                queries=[aip.Query(
                    embedding=query_embedding,
                    top_k=k,
                    filter=filter
                )]
            )
            
            # Process results
            results = []
            for match in response.matches:
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query Matching Engine: {e}")
            return []
    
    def _save_embeddings_to_gcs(self, embeddings_data: List[Dict[str, Any]]) -> None:
        """Save embeddings to GCS"""
        try:
            from google.cloud import storage
            
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            
            # Save embeddings
            embeddings_blob = bucket.blob(self.embeddings_path)
            embeddings_blob.upload_from_string(
                json.dumps(embeddings_data, indent=2),
                content_type='application/json'
            )
            
            # Save metadata
            metadata = {
                "total_documents": len(embeddings_data),
                "last_updated": datetime.utcnow().isoformat(),
                "dimensions": len(embeddings_data[0]["embedding"]) if embeddings_data else 0
            }
            
            metadata_blob = bucket.blob(self.metadata_path)
            metadata_blob.upload_from_string(
                json.dumps(metadata, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"Saved {len(embeddings_data)} embeddings to GCS")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings to GCS: {e}")
            raise
    
    def _update_index_contents(self) -> None:
        """Update index contents with new embeddings"""
        try:
            logger.info("Updating index contents")
            
            # Update index
            update_request = aip.UpdateIndexRequest(
                index=f"projects/{self.project_id}/locations/{self.location}/indexes/{self.index_id}",
                index_update=aip.Index(
                    metadata={
                        "contentsDeltaUri": f"gs://{self.gcs_bucket}/{self.embeddings_path}",
                        "isCompleteOverwrite": True
                    }
                )
            )
            
            operation = self.index_client.update_index(update_request)
            
            # Wait for update
            while not operation.done():
                time.sleep(30)
                operation = self.index_client.get_operation(operation.name)
                logger.info(f"Index update status: {operation.metadata}")
            
            if operation.error:
                raise Exception(f"Index update failed: {operation.error}")
            
            logger.info("Index contents updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update index contents: {e}")
            raise
    
    def get_index_status(self) -> Dict[str, Any]:
        """Get index and endpoint status"""
        try:
            status = {
                "index_id": self.index_id,
                "index_endpoint_id": self.index_endpoint_id,
                "deployed_index_id": self.deployed_index_id,
                "status": "unknown"
            }
            
            if self.index_id:
                index = self.index_client.get_index(
                    name=f"projects/{self.project_id}/locations/{self.location}/indexes/{self.index_id}"
                )
                status["index_status"] = index.state.name
                status["index_metadata"] = index.metadata
            
            if self.index_endpoint_id:
                endpoint = self.index_endpoint_client.get_index_endpoint(
                    name=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_endpoint_id}"
                )
                status["endpoint_status"] = endpoint.state.name
                status["deployed_indexes"] = [d.id for d in endpoint.deployed_indexes]
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get index status: {e}")
            return {"error": str(e)}
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            logger.info("Cleaning up Matching Engine resources")
            
            # Delete deployed index
            if self.index_endpoint_id and self.deployed_index_id:
                self.index_endpoint_client.undeploy_index(
                    index_endpoint=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_endpoint_id}",
                    deployed_index_id=self.deployed_index_id
                )
                logger.info("Deployed index undeployed")
            
            # Delete index endpoint
            if self.index_endpoint_id:
                self.index_endpoint_client.delete_index_endpoint(
                    name=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_endpoint_id}"
                )
                logger.info("Index endpoint deleted")
            
            # Delete index
            if self.index_id:
                self.index_client.delete_index(
                    name=f"projects/{self.project_id}/locations/{self.location}/indexes/{self.index_id}"
                )
                logger.info("Index deleted")
            
        except Exception as e:
            logger.error(f"Failed to cleanup resources: {e}")
            raise
