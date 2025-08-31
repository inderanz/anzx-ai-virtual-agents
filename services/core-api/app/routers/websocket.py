"""
WebSocket endpoints for real-time chat communication
"""

import logging
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..utils.database import get_db
from ..services.chat_widget_service import chat_widget_service
from ..models.user import ChatWidget

logger = logging.getLogger(__name__)

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.widget_connections: Dict[str, list] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, widget_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if widget_id not in self.widget_connections:
            self.widget_connections[widget_id] = []
        self.widget_connections[widget_id].append(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} for widget {widget_id}")
    
    def disconnect(self, connection_id: str, widget_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if widget_id in self.widget_connections:
            self.widget_connections[widget_id] = [
                conn for conn in self.widget_connections[widget_id] 
                if conn != connection_id
            ]
            if not self.widget_connections[widget_id]:
                del self.widget_connections[widget_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: str, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(message)
    
    async def send_to_widget(self, message: str, widget_id: str):
        if widget_id in self.widget_connections:
            for connection_id in self.widget_connections[widget_id]:
                await self.send_personal_message(message, connection_id)

manager = ConnectionManager()


@router.websocket("/api/chat-widget/ws/{widget_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for chat widget real-time communication"""
    
    connection_id = f"{widget_id}_{id(websocket)}"
    
    try:
        await manager.connect(websocket, connection_id, widget_id)
        
        # Wait for authentication
        auth_data = await websocket.receive_text()
        auth_message = json.loads(auth_data)
        
        if auth_message.get("type") != "auth":
            await websocket.send_text(json.dumps({
                "type": "auth_failed",
                "message": "Authentication required"
            }))
            await websocket.close(code=4001)
            return
        
        # Validate widget credentials
        api_key = auth_message.get("api_key")
        if not api_key:
            await websocket.send_text(json.dumps({
                "type": "auth_failed",
                "message": "API key required"
            }))
            await websocket.close(code=4001)
            return
        
        # Validate widget
        widget = db.query(ChatWidget).filter(
            ChatWidget.id == widget_id,
            ChatWidget.api_key == api_key,
            ChatWidget.is_active == True
        ).first()
        
        if not widget:
            await websocket.send_text(json.dumps({
                "type": "auth_failed",
                "message": "Invalid widget credentials"
            }))
            await websocket.close(code=4001)
            return
        
        # Send authentication success
        await websocket.send_text(json.dumps({
            "type": "auth_success",
            "message": "Authenticated successfully"
        }))
        
        # Handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                await handle_websocket_message(
                    websocket=websocket,
                    connection_id=connection_id,
                    widget_id=widget_id,
                    message_data=message_data,
                    db=db
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(connection_id, widget_id)


async def handle_websocket_message(
    websocket: WebSocket,
    connection_id: str,
    widget_id: str,
    message_data: Dict[str, Any],
    db: Session
):
    """Handle incoming WebSocket messages"""
    
    message_type = message_data.get("type")
    
    if message_type == "message":
        # Handle chat message
        try:
            # Send typing indicator
            await websocket.send_text(json.dumps({
                "type": "typing",
                "typing": True
            }))
            
            # Process the message
            result = await chat_widget_service.handle_chat_message(
                db=db,
                widget_id=widget_id,
                conversation_id=message_data.get("conversation_id"),
                message=message_data.get("content"),
                visitor_info=message_data.get("visitor_info")
            )
            
            # Stop typing indicator
            await websocket.send_text(json.dumps({
                "type": "typing",
                "typing": False
            }))
            
            # Send AI response if available
            if "ai_response" in result:
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": result["ai_response"]["content"],
                    "citations": result["ai_response"].get("citations", []),
                    "message_id": result["ai_response"]["message_id"],
                    "timestamp": result["ai_response"]["timestamp"]
                }))
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Failed to process message"
            }))
    
    elif message_type == "ping":
        # Heartbeat response
        await websocket.send_text(json.dumps({
            "type": "pong"
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))


@router.get("/api/chat-widget/public/messages/{conversation_id}")
async def get_conversation_messages(
    conversation_id: str,
    widget_id: str = None,
    api_key: str = None,
    last_message_id: str = None,
    db: Session = Depends(get_db)
):
    """Get conversation messages for polling fallback"""
    
    # This endpoint would be used for HTTP polling fallback
    # Implementation would fetch new messages since last_message_id
    
    return {
        "messages": [],
        "has_more": False
    }