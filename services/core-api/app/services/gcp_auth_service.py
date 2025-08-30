"""
GCP Authentication Service with Workload Identity Federation support
"""

import logging
import os
from typing import Optional, Dict, Any
from google.auth import default, impersonated_credentials
from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
import google.auth.transport.requests
from google.oauth2 import service_account
import requests
import json

from ..config.vertex_ai import vertex_ai_config

logger = logging.getLogger(__name__)


class GCPAuthService:
    """
    GCP Authentication service supporting multiple authentication methods:
    - Workload Identity Federation (GKE)
    - Default Service Account (Cloud Run)
    - Service Account Key (local development)
    """
    
    def __init__(self):
        self.config = vertex_ai_config
        self._credentials: Optional[Credentials] = None
        self._project_id: Optional[str] = None
        self._runtime_environment = self.config.RUNTIME_ENVIRONMENT
        
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize credentials based on runtime environment"""
        try:
            if self._runtime_environment == "gke":
                self._initialize_workload_identity()
            elif self._runtime_environment == "cloudrun":
                self._initialize_cloudrun_auth()
            else:
                self._initialize_local_auth()
                
            logger.info(f"GCP authentication initialized for {self._runtime_environment}")
            
        except Exception as e:
            logger.error(f"Failed to initialize GCP authentication: {e}")
            raise
    
    def _initialize_workload_identity(self):
        """Initialize Workload Identity Federation for GKE"""
        try:
            # Verify we're running in GKE with Workload Identity
            if not self._is_gke_environment():
                raise ValueError("Not running in GKE environment")
            
            # Get default credentials (should use Workload Identity)
            credentials, project_id = default(scopes=self.config.REQUIRED_SCOPES)
            
            # Verify the credentials are using the expected service account
            if hasattr(credentials, 'service_account_email'):
                expected_sa = self.config.GOOGLE_SERVICE_ACCOUNT
                actual_sa = credentials.service_account_email
                
                if actual_sa != expected_sa:
                    logger.warning(
                        f"Service account mismatch. Expected: {expected_sa}, "
                        f"Actual: {actual_sa}"
                    )
            
            self._credentials = credentials
            self._project_id = project_id or self.config.PROJECT_ID
            
            logger.info(
                f"Workload Identity initialized. "
                f"Project: {self._project_id}, "
                f"K8s SA: {self.config.KUBERNETES_SERVICE_ACCOUNT}, "
                f"Google SA: {self.config.GOOGLE_SERVICE_ACCOUNT}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Workload Identity: {e}")
            raise
    
    def _initialize_cloudrun_auth(self):
        """Initialize authentication for Cloud Run"""
        try:
            # Verify we're running in Cloud Run
            if not self._is_cloudrun_environment():
                raise ValueError("Not running in Cloud Run environment")
            
            # Get default credentials (uses attached service account)
            credentials, project_id = default(scopes=self.config.REQUIRED_SCOPES)
            
            self._credentials = credentials
            self._project_id = project_id or self.config.PROJECT_ID
            
            # Get service account info from metadata server
            sa_info = self._get_service_account_info()
            
            logger.info(
                f"Cloud Run authentication initialized. "
                f"Project: {self._project_id}, "
                f"Service Account: {sa_info.get('email', 'unknown')}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Run authentication: {e}")
            raise
    
    def _initialize_local_auth(self):
        """Initialize authentication for local development"""
        try:
            # Try Application Default Credentials first
            try:
                credentials, project_id = default(scopes=self.config.REQUIRED_SCOPES)
                self._credentials = credentials
                self._project_id = project_id or self.config.PROJECT_ID
                
                logger.info(f"Local ADC authentication initialized. Project: {self._project_id}")
                return
                
            except DefaultCredentialsError:
                logger.warning("ADC not available, trying service account key")
            
            # Fall back to service account key if available
            service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if service_account_path and os.path.exists(service_account_path):
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=self.config.REQUIRED_SCOPES
                )
                
                self._credentials = credentials
                self._project_id = credentials.project_id or self.config.PROJECT_ID
                
                logger.info(f"Service account key authentication initialized. Project: {self._project_id}")
                return
            
            raise ValueError("No valid authentication method found for local development")
            
        except Exception as e:
            logger.error(f"Failed to initialize local authentication: {e}")
            raise
    
    def _is_gke_environment(self) -> bool:
        """Check if running in GKE environment"""
        try:
            # Check for Kubernetes service account token
            token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
            if not os.path.exists(token_path):
                return False
            
            # Check for GKE-specific metadata
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/cluster-name"
            headers = {"Metadata-Flavor": "Google"}
            
            response = requests.get(metadata_url, headers=headers, timeout=5)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _is_cloudrun_environment(self) -> bool:
        """Check if running in Cloud Run environment"""
        try:
            # Cloud Run sets specific environment variables
            if os.getenv("K_SERVICE") and os.getenv("K_REVISION"):
                return True
            
            # Check metadata server for Cloud Run specific info
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/region"
            headers = {"Metadata-Flavor": "Google"}
            
            response = requests.get(metadata_url, headers=headers, timeout=5)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _get_service_account_info(self) -> Dict[str, Any]:
        """Get service account information from metadata server"""
        try:
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/"
            headers = {"Metadata-Flavor": "Google"}
            
            # Get service account email
            email_response = requests.get(
                f"{metadata_url}email",
                headers=headers,
                timeout=5
            )
            
            # Get service account scopes
            scopes_response = requests.get(
                f"{metadata_url}scopes",
                headers=headers,
                timeout=5
            )
            
            return {
                "email": email_response.text if email_response.status_code == 200 else "unknown",
                "scopes": scopes_response.text.split('\n') if scopes_response.status_code == 200 else []
            }
            
        except Exception as e:
            logger.warning(f"Failed to get service account info: {e}")
            return {}
    
    def get_credentials(self) -> Credentials:
        """Get authenticated credentials"""
        if not self._credentials:
            raise ValueError("Credentials not initialized")
        
        # Refresh credentials if needed
        try:
            if not self._credentials.valid:
                request = google.auth.transport.requests.Request()
                self._credentials.refresh(request)
                
        except RefreshError as e:
            logger.error(f"Failed to refresh credentials: {e}")
            raise
        
        return self._credentials
    
    def get_project_id(self) -> str:
        """Get the current project ID"""
        return self._project_id or self.config.PROJECT_ID
    
    def get_access_token(self) -> str:
        """Get current access token"""
        credentials = self.get_credentials()
        
        if not credentials.token:
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
        
        return credentials.token
    
    def create_impersonated_credentials(
        self,
        target_service_account: str,
        target_scopes: Optional[list] = None
    ) -> impersonated_credentials.Credentials:
        """
        Create impersonated credentials for service account impersonation
        
        Args:
            target_service_account: Email of the service account to impersonate
            target_scopes: Scopes for the impersonated credentials
            
        Returns:
            Impersonated credentials
        """
        try:
            source_credentials = self.get_credentials()
            target_scopes = target_scopes or self.config.REQUIRED_SCOPES
            
            impersonated_creds = impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=target_service_account,
                target_scopes=target_scopes
            )
            
            logger.info(f"Created impersonated credentials for: {target_service_account}")
            return impersonated_creds
            
        except Exception as e:
            logger.error(f"Failed to create impersonated credentials: {e}")
            raise
    
    def verify_permissions(self, required_permissions: list) -> Dict[str, bool]:
        """
        Verify that the current credentials have required permissions
        
        Args:
            required_permissions: List of required IAM permissions
            
        Returns:
            Dictionary mapping permissions to whether they're granted
        """
        try:
            from google.cloud import resourcemanager_v3
            
            # Create Resource Manager client to test permissions
            client = resourcemanager_v3.ProjectsClient(credentials=self.get_credentials())
            
            # Test permissions on the project
            project_name = f"projects/{self.get_project_id()}"
            
            request = resourcemanager_v3.TestIamPermissionsRequest(
                resource=project_name,
                permissions=required_permissions
            )
            
            response = client.test_iam_permissions(request=request)
            granted_permissions = set(response.permissions)
            
            return {
                permission: permission in granted_permissions
                for permission in required_permissions
            }
            
        except Exception as e:
            logger.error(f"Failed to verify permissions: {e}")
            return {permission: False for permission in required_permissions}
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get comprehensive authentication status"""
        try:
            credentials = self.get_credentials()
            sa_info = self._get_service_account_info()
            
            # Test basic permissions
            vertex_ai_permissions = [
                "aiplatform.endpoints.predict",
                "aiplatform.models.predict",
                "discoveryengine.conversations.converse"
            ]
            
            permissions_status = self.verify_permissions(vertex_ai_permissions)
            
            return {
                "status": "authenticated",
                "runtime_environment": self._runtime_environment,
                "project_id": self.get_project_id(),
                "credentials_valid": credentials.valid if credentials else False,
                "service_account_email": sa_info.get("email", "unknown"),
                "available_scopes": sa_info.get("scopes", []),
                "required_scopes": self.config.REQUIRED_SCOPES,
                "permissions_status": permissions_status,
                "workload_identity_configured": self._runtime_environment == "gke",
                "timestamp": os.environ.get("REQUEST_ID", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Failed to get auth status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "runtime_environment": self._runtime_environment
            }


# Global authentication service instance
gcp_auth_service = GCPAuthService()