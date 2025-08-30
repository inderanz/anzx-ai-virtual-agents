"""
JWT token handling for internal API authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """JWT token handler for internal authentication"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key")
        self.algorithm = "HS256"
        self.expiration_hours = 24
    
    def create_access_token(
        self,
        user_id: str,
        email: str,
        organization_id: Optional[str] = None,
        roles: Optional[list] = None,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User identifier
            email: User email
            organization_id: Organization identifier
            roles: User roles
            custom_claims: Additional claims
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expire = now + timedelta(hours=self.expiration_hours)
        
        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": expire,
            "type": "access"
        }
        
        if organization_id:
            payload["org_id"] = organization_id
        
        if roles:
            payload["roles"] = roles
        
        if custom_claims:
            payload.update(custom_claims)
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create refresh token for token renewal
        
        Args:
            user_id: User identifier
            
        Returns:
            Refresh token string
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=30)  # Longer expiration for refresh tokens
        
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expire,
            "type": "refresh"
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Refresh token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token"
            )
    
    def verify_refresh_token(self, token: str) -> str:
        """
        Verify refresh token and extract user ID
        
        Args:
            token: Refresh token string
            
        Returns:
            User ID
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload["sub"]
            
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


# Global JWT handler instance
jwt_handler = JWTHandler()