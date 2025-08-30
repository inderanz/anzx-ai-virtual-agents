"""
Usage tracking middleware for automatic metering
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from ..models.database import SessionLocal
from ..services.usage_service import usage_service
from ..auth.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track API usage"""
    
    def __init__(self, app, track_all_requests: bool = False):
        super().__init__(app)
        self.track_all_requests = track_all_requests
        
        # Endpoints that should be tracked for usage
        self.tracked_endpoints = {
            "/api/v1/chat/",
            "/api/v1/assistants/",
            "/api/v1/conversations/",
            "/api/v1/knowledge/"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track usage"""
        start_time = time.time()
        
        # Check if this endpoint should be tracked
        should_track = self._should_track_request(request)
        
        # Get user info if available
        user_info = None
        if should_track:
            try:
                # Try to get current user without raising exceptions
                user_info = await self._get_user_info(request)
            except Exception:
                pass  # Continue without user info
        
        # Process request
        response = await call_next(request)
        
        # Track usage if applicable
        if should_track and user_info and user_info.get("organization_id"):
            try:
                await self._track_request_usage(
                    request=request,
                    response=response,
                    user_info=user_info,
                    duration_ms=int((time.time() - start_time) * 1000)
                )
            except Exception as e:
                logger.error(f"Failed to track usage: {e}")
        
        return response
    
    def _should_track_request(self, request: Request) -> bool:
        """Determine if request should be tracked"""
        if self.track_all_requests:
            return True
        
        path = request.url.path
        
        # Check if path starts with any tracked endpoint
        return any(path.startswith(endpoint) for endpoint in self.tracked_endpoints)
    
    async def _get_user_info(self, request: Request) -> dict:
        """Extract user information from request"""
        try:
            # Get authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # This is a simplified version - in practice, you'd use the actual auth logic
            # For now, we'll return None and handle usage tracking in the endpoints directly
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract user info: {e}")
            return None
    
    async def _track_request_usage(
        self,
        request: Request,
        response: Response,
        user_info: dict,
        duration_ms: int
    ):
        """Track usage for the request"""
        try:
            db = SessionLocal()
            
            # Determine usage metrics based on endpoint
            tokens_input = 0
            tokens_output = 0
            cost = 0.0
            
            # Extract usage info from response headers if available
            if hasattr(response, 'headers'):
                tokens_input = int(response.headers.get('X-Tokens-Input', 0))
                tokens_output = int(response.headers.get('X-Tokens-Output', 0))
                cost = float(response.headers.get('X-Cost', 0.0))
            
            # Track the usage
            await usage_service.track_message_usage(
                db=db,
                organization_id=user_info["organization_id"],
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost
            )
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to track request usage: {e}")


class UsageTracker:
    """Helper class for manual usage tracking in endpoints"""
    
    @staticmethod
    async def track_ai_interaction(
        db: Session,
        organization_id: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost: float = 0.0,
        model: str = None
    ) -> dict:
        """
        Track AI interaction usage
        
        Args:
            db: Database session
            organization_id: Organization ID
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            cost: Cost of the interaction
            model: Model used
            
        Returns:
            Usage statistics
        """
        try:
            usage_stats = await usage_service.track_message_usage(
                db=db,
                organization_id=organization_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost
            )
            
            # Log usage for monitoring
            logger.info(
                f"AI interaction tracked - Org: {organization_id}, "
                f"Tokens: {tokens_input + tokens_output}, Cost: ${cost:.6f}, "
                f"Model: {model}"
            )
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Failed to track AI interaction: {e}")
            raise
    
    @staticmethod
    async def check_usage_limits(
        db: Session,
        organization_id: str,
        required_tokens: int = 0
    ) -> dict:
        """
        Check if organization can perform action within usage limits
        
        Args:
            db: Database session
            organization_id: Organization ID
            required_tokens: Tokens required for the action
            
        Returns:
            Limit check results
        """
        try:
            limit_status = await usage_service.check_usage_limits(db, organization_id)
            
            # Check if action would exceed limits
            can_proceed = True
            if limit_status["any_over_limit"]:
                can_proceed = False
            
            # Check token limit specifically if provided
            if required_tokens > 0:
                token_status = limit_status["limit_status"].get("tokens_per_month", {})
                if not token_status.get("unlimited", False):
                    remaining_tokens = token_status["limit"] - token_status["used"]
                    if required_tokens > remaining_tokens:
                        can_proceed = False
            
            return {
                **limit_status,
                "can_proceed": can_proceed,
                "required_tokens": required_tokens
            }
            
        except Exception as e:
            logger.error(f"Failed to check usage limits: {e}")
            # Allow action to proceed if check fails
            return {"can_proceed": True, "error": str(e)}
    
    @staticmethod
    def calculate_token_cost(
        tokens_input: int,
        tokens_output: int,
        model: str = "gemini-pro"
    ) -> float:
        """
        Calculate cost for token usage
        
        Args:
            tokens_input: Input tokens
            tokens_output: Output tokens
            model: Model used
            
        Returns:
            Cost in AUD
        """
        # Pricing per 1K tokens (approximate Vertex AI pricing in AUD)
        pricing = {
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-ultra": {"input": 0.001, "output": 0.003},
            "text-embedding-004": {"input": 0.0001, "output": 0.0001}
        }
        
        model_pricing = pricing.get(model, pricing["gemini-pro"])
        
        input_cost = (tokens_input / 1000) * model_pricing["input"]
        output_cost = (tokens_output / 1000) * model_pricing["output"]
        
        return input_cost + output_cost


# Global usage tracker instance
usage_tracker = UsageTracker()