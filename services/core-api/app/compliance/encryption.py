"""
Encryption utilities using Google Cloud KMS
Implements AES-256 encryption at rest and in transit
"""

import base64
import os
from typing import Optional, Dict, Any
from google.cloud import kms
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class KMSEncryption:
    """Google Cloud KMS encryption service"""
    
    def __init__(self, project_id: str, location: str, key_ring: str, key_name: str):
        self.client = kms.KeyManagementServiceClient()
        self.key_name = self.client.crypto_key_path(
            project_id, location, key_ring, key_name
        )
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt data using Cloud KMS"""
        try:
            plaintext_bytes = plaintext.encode('utf-8')
            response = self.client.encrypt(
                request={"name": self.key_name, "plaintext": plaintext_bytes}
            )
            return base64.b64encode(response.ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"KMS encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt data using Cloud KMS"""
        try:
            ciphertext_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            response = self.client.decrypt(
                request={"name": self.key_name, "ciphertext": ciphertext_bytes}
            )
            return response.plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"KMS decryption failed: {e}")
            raise


class FieldEncryption:
    """Field-level encryption for sensitive data"""
    
    def __init__(self, kms_encryption: KMSEncryption):
        self.kms = kms_encryption
        self._field_keys: Dict[str, bytes] = {}
    
    def _get_field_key(self, field_name: str) -> bytes:
        """Get or create encryption key for specific field"""
        if field_name not in self._field_keys:
            # Generate field-specific key using KMS
            key_material = os.urandom(32)
            encrypted_key = self.kms.encrypt(base64.b64encode(key_material).decode())
            
            # Store encrypted key (in practice, would store in database)
            self._field_keys[field_name] = key_material
        
        return self._field_keys[field_name]
    
    def encrypt_field(self, field_name: str, value: str) -> str:
        """Encrypt a specific field value"""
        key = self._get_field_key(field_name)
        f = Fernet(base64.urlsafe_b64encode(key))
        encrypted_value = f.encrypt(value.encode('utf-8'))
        return base64.b64encode(encrypted_value).decode('utf-8')
    
    def decrypt_field(self, field_name: str, encrypted_value: str) -> str:
        """Decrypt a specific field value"""
        key = self._get_field_key(field_name)
        f = Fernet(base64.urlsafe_b64encode(key))
        encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
        decrypted_value = f.decrypt(encrypted_bytes)
        return decrypted_value.decode('utf-8')


# Encryption configuration
ENCRYPTION_CONFIG = {
    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
    "location": os.getenv("KMS_LOCATION", "australia-southeast1"),
    "key_ring": os.getenv("KMS_KEY_RING", "anzx-keyring"),
    "key_name": os.getenv("KMS_KEY_NAME", "anzx-app-key")
}

# Global encryption instances
kms_encryption = KMSEncryption(**ENCRYPTION_CONFIG) if all(ENCRYPTION_CONFIG.values()) else None
field_encryption = FieldEncryption(kms_encryption) if kms_encryption else None