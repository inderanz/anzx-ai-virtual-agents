"""
Firebase Authentication integration
Handles magic link and Google OAuth authentication
"""

import os
import json
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class FirebaseAuth:
    """Firebase Authentication service"""
    
    def __init__(self):
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase
            firebase_config = os.getenv("FIREBASE_CONFIG")
            if firebase_config:
                config_dict = json.loads(firebase_config)
                cred = credentials.Certificate(config_dict)
            else:
                # Use default credentials in production
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized")
    
    async def verify_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Dict containing user information
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            
            user_info = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "provider": decoded_token.get("firebase", {}).get("sign_in_provider"),
                "custom_claims": decoded_token.get("custom_claims", {})
            }
            
            logger.info(f"Token verified for user: {user_info['uid']}")
            return user_info
            
        except auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def create_custom_token(self, uid: str, claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create custom token for user
        
        Args:
            uid: User ID
            claims: Custom claims to include
            
        Returns:
            Custom token string
        """
        try:
            custom_token = auth.create_custom_token(uid, claims)
            logger.info(f"Custom token created for user: {uid}")
            return custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"Custom token creation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create authentication token"
            )
    
    async def set_custom_claims(self, uid: str, claims: Dict[str, Any]) -> None:
        """
        Set custom claims for user (roles, permissions, etc.)
        
        Args:
            uid: User ID
            claims: Custom claims to set
        """
        try:
            auth.set_custom_user_claims(uid, claims)
            logger.info(f"Custom claims set for user {uid}: {claims}")
        except Exception as e:
            logger.error(f"Failed to set custom claims for {uid}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user permissions"
            )
    
    async def get_user(self, uid: str) -> Dict[str, Any]:
        """
        Get user information from Firebase
        
        Args:
            uid: User ID
            
        Returns:
            User information dictionary
        """
        try:
            user_record = auth.get_user(uid)
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "email_verified": user_record.email_verified,
                "display_name": user_record.display_name,
                "photo_url": user_record.photo_url,
                "disabled": user_record.disabled,
                "custom_claims": user_record.custom_claims or {},
                "provider_data": [
                    {
                        "provider_id": provider.provider_id,
                        "uid": provider.uid,
                        "email": provider.email,
                        "display_name": provider.display_name,
                        "photo_url": provider.photo_url
                    }
                    for provider in user_record.provider_data
                ]
            }
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user information"
            )
    
    async def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
        email_verified: bool = False
    ) -> str:
        """
        Create new user in Firebase
        
        Args:
            email: User email
            password: User password (optional for magic link)
            display_name: User display name
            email_verified: Whether email is verified
            
        Returns:
            User ID
        """
        try:
            user_args = {
                "email": email,
                "email_verified": email_verified
            }
            
            if password:
                user_args["password"] = password
            
            if display_name:
                user_args["display_name"] = display_name
            
            user_record = auth.create_user(**user_args)
            logger.info(f"User created: {user_record.uid}")
            return user_record.uid
            
        except auth.EmailAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def generate_email_verification_link(self, email: str) -> str:
        """
        Generate email verification link
        
        Args:
            email: User email
            
        Returns:
            Verification link
        """
        try:
            link = auth.generate_email_verification_link(email)
            logger.info(f"Email verification link generated for: {email}")
            return link
        except Exception as e:
            logger.error(f"Failed to generate verification link: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate verification link"
            )
    
    async def generate_password_reset_link(self, email: str) -> str:
        """
        Generate password reset link
        
        Args:
            email: User email
            
        Returns:
            Password reset link
        """
        try:
            link = auth.generate_password_reset_link(email)
            logger.info(f"Password reset link generated for: {email}")
            return link
        except Exception as e:
            logger.error(f"Failed to generate password reset link: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate password reset link"
            )


# Global Firebase auth instance
firebase_auth = FirebaseAuth()