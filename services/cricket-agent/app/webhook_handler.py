"""
PlayHQ Webhook Handler
Handles incoming webhooks from PlayHQ for real-time updates
"""

import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from .config import get_settings
from .webhook_models import WebhookRequest, WebhookResponse, WebhookEventType
from .observability import get_logger, get_metrics
from agent.tools.normalize import normalize_playhq_data, generate_snippet
from agent.tools.vector_client import get_vector_client

logger = get_logger(__name__)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify PlayHQ webhook signature"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Failed to verify webhook signature: {e}")
        return False

async def process_webhook(request: Request) -> WebhookResponse:
    """Process incoming PlayHQ webhook"""
    try:
        settings = get_settings()
        
        # Check if private mode is enabled
        if settings.playhq_mode != "private":
            raise HTTPException(status_code=403, detail="Webhook mode not enabled")
        
        # Get webhook secret
        if not settings.playhq_webhook_secret:
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        # Get signature from headers
        signature = request.headers.get("X-PlayHQ-Signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Missing webhook signature")
        
        # Get request body
        body = await request.body()
        
        # Verify signature
        if not verify_webhook_signature(body, signature, settings.playhq_webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook payload
        try:
            payload_data = json.loads(body.decode('utf-8'))
            webhook_request = WebhookRequest(**payload_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {e}")
        
        logger.info(
            "Webhook received",
            event_type=webhook_request.event_type,
            timestamp=webhook_request.timestamp
        )
        
        # Process based on event type
        processed_count = 0
        errors = []
        
        try:
            if webhook_request.event_type == WebhookEventType.FIXTURE_UPDATE:
                processed_count = await _process_fixture_update(webhook_request)
            elif webhook_request.event_type == WebhookEventType.SCORECARD_UPDATE:
                processed_count = await _process_scorecard_update(webhook_request)
            elif webhook_request.event_type == WebhookEventType.LADDER_UPDATE:
                processed_count = await _process_ladder_update(webhook_request)
            elif webhook_request.event_type == WebhookEventType.ROSTER_UPDATE:
                processed_count = await _process_roster_update(webhook_request)
            else:
                raise ValueError(f"Unknown event type: {webhook_request.event_type}")
                
        except Exception as e:
            logger.error(f"Failed to process webhook: {e}")
            errors.append(str(e))
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_request(
            latency_ms=0,  # Webhook processing is typically fast
            success=len(errors) == 0,
            intent="webhook_processing"
        )
        
        return WebhookResponse(
            success=len(errors) == 0,
            message=f"Processed {processed_count} records",
            processed_count=processed_count,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def _process_fixture_update(webhook_request: WebhookRequest) -> int:
    """Process fixture update webhook"""
    try:
        fixture_data = webhook_request.get_typed_data()
        
        # Normalize fixture data
        normalized_fixture = normalize_fixture(fixture_data.dict())
        
        # Generate snippet
        snippet = generate_fixture_snippet(normalized_fixture)
        
        # Prepare document for vector store
        doc = {
            "id": f"fixture_{fixture_data.fixture_id}",
            "text": snippet,
            "metadata": {
                "team_id": fixture_data.team_id,
                "season_id": fixture_data.season_id,
                "grade_id": fixture_data.grade_id,
                "type": "fixture",
                "fixture_id": fixture_data.fixture_id,
                "status": fixture_data.status
            }
        }
        
        # Upsert to vector store
        vector_client = get_vector_client()
        vector_client.upsert([doc])
        
        logger.info(
            "Fixture update processed",
            fixture_id=fixture_data.fixture_id,
            team_id=fixture_data.team_id,
            status=fixture_data.status
        )
        
        return 1
        
    except Exception as e:
        logger.error(f"Failed to process fixture update: {e}")
        raise

async def _process_scorecard_update(webhook_request: WebhookRequest) -> int:
    """Process scorecard update webhook"""
    try:
        scorecard_data = webhook_request.get_typed_data()
        
        # Only process completed scorecards
        if not scorecard_data.is_completed:
            logger.info("Scorecard not completed, skipping", fixture_id=scorecard_data.fixture_id)
            return 0
        
        # Normalize scorecard data
        normalized_scorecard = normalize_scorecard(scorecard_data.dict())
        
        # Generate snippet
        snippet = generate_scorecard_snippet(normalized_scorecard)
        
        # Prepare document for vector store
        doc = {
            "id": f"scorecard_{scorecard_data.fixture_id}",
            "text": snippet,
            "metadata": {
                "team_id": scorecard_data.team_id,
                "season_id": scorecard_data.season_id,
                "grade_id": scorecard_data.grade_id,
                "type": "scorecard",
                "fixture_id": scorecard_data.fixture_id,
                "is_completed": True
            }
        }
        
        # Upsert to vector store
        vector_client = get_vector_client()
        vector_client.upsert([doc])
        
        logger.info(
            "Scorecard update processed",
            fixture_id=scorecard_data.fixture_id,
            team_id=scorecard_data.team_id
        )
        
        return 1
        
    except Exception as e:
        logger.error(f"Failed to process scorecard update: {e}")
        raise

async def _process_ladder_update(webhook_request: WebhookRequest) -> int:
    """Process ladder update webhook"""
    try:
        ladder_data = webhook_request.get_typed_data()
        
        # Normalize ladder data
        normalized_ladder = normalize_ladder(ladder_data.dict())
        
        # Generate snippet
        snippet = generate_ladder_snippet(normalized_ladder)
        
        # Prepare document for vector store
        doc = {
            "id": f"ladder_{ladder_data.grade_id}_{ladder_data.team_id}",
            "text": snippet,
            "metadata": {
                "team_id": ladder_data.team_id,
                "season_id": ladder_data.season_id,
                "grade_id": ladder_data.grade_id,
                "type": "ladder",
                "position": ladder_data.position
            }
        }
        
        # Upsert to vector store
        vector_client = get_vector_client()
        vector_client.upsert([doc])
        
        logger.info(
            "Ladder update processed",
            grade_id=ladder_data.grade_id,
            team_id=ladder_data.team_id,
            position=ladder_data.position
        )
        
        return 1
        
    except Exception as e:
        logger.error(f"Failed to process ladder update: {e}")
        raise

async def _process_roster_update(webhook_request: WebhookRequest) -> int:
    """Process roster update webhook"""
    try:
        roster_data = webhook_request.get_typed_data()
        
        # Normalize roster data
        normalized_roster = normalize_roster(roster_data.dict())
        
        # Generate snippet
        snippet = generate_roster_snippet(normalized_roster)
        
        # Prepare document for vector store
        doc = {
            "id": f"roster_{roster_data.team_id}",
            "text": snippet,
            "metadata": {
                "team_id": roster_data.team_id,
                "season_id": roster_data.season_id,
                "grade_id": roster_data.grade_id,
                "type": "roster"
            }
        }
        
        # Upsert to vector store
        vector_client = get_vector_client()
        vector_client.upsert([doc])
        
        logger.info(
            "Roster update processed",
            team_id=roster_data.team_id,
            player_count=len(roster_data.players)
        )
        
        return 1
        
    except Exception as e:
        logger.error(f"Failed to process roster update: {e}")
        raise
