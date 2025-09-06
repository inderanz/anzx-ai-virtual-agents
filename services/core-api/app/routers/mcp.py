"""
MCP (Model Context Protocol) API Endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..utils.database import get_db
from ..middleware.auth import get_current_user, get_organization_id
from ..services.mcp_server_manager import mcp_server_manager
from ..services.mcp_tool_registry import mcp_tool_registry
from ..services.mcp_integrations import mcp_integration_manager
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


# Pydantic models
class MCPServerConfig(BaseModel):
    name: str = Field(..., description="Server name")
    command: str = Field(..., description="Command to run")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    working_directory: Optional[str] = Field(None, description="Working directory")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")
    max_retries: Optional[int] = Field(3, description="Maximum retry attempts")
    health_check_interval: Optional[int] = Field(60, description="Health check interval")
    auto_restart: Optional[bool] = Field(True, description="Auto-restart on failure")
    security_sandbox: Optional[bool] = Field(True, description="Enable security sandbox")
    allowed_capabilities: Optional[List[str]] = Field(default_factory=list, description="Allowed capabilities")


class ToolExecutionRequest(BaseModel):
    tool_id: str = Field(..., description="Tool ID")
    input_parameters: Dict[str, Any] = Field(..., description="Input parameters")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class ToolApprovalRequest(BaseModel):
    execution_id: str = Field(..., description="Execution ID")
    approval_reason: Optional[str] = Field(None, description="Reason for approval")


class IntegrationSetupRequest(BaseModel):
    integration_name: str = Field(..., description="Integration name")
    config: Dict[str, Any] = Field(..., description="Integration configuration")


# Server management endpoints
@router.post("/servers", response_model=Dict[str, Any])
async def register_mcp_server(
    server_config: MCPServerConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Register a new MCP server"""
    try:
        result = await mcp_server_manager.register_server(
            db=db,
            organization_id=organization_id,
            server_config=server_config.dict()
        )
        
        return result
        
    except Exception as e:
        logger.error(f"MCP server registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/servers", response_model=List[Dict[str, Any]])
async def get_mcp_servers_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get status of all MCP servers"""
    try:
        status_list = await mcp_server_manager.get_all_servers_status()
        return status_list
        
    except Exception as e:
        logger.error(f"Failed to get MCP servers status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get servers status"
        )


@router.get("/servers/{server_name}/status", response_model=Dict[str, Any])
async def get_mcp_server_status(
    server_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get specific MCP server status"""
    try:
        status = await mcp_server_manager.get_server_status(server_name)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get server status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/servers/{server_name}/start", response_model=Dict[str, Any])
async def start_mcp_server(
    server_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Start an MCP server"""
    try:
        result = await mcp_server_manager.start_server(server_name)
        return result
        
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/servers/{server_name}/stop", response_model=Dict[str, Any])
async def stop_mcp_server(
    server_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Stop an MCP server"""
    try:
        result = await mcp_server_manager.stop_server(server_name)
        return result
        
    except Exception as e:
        logger.error(f"Failed to stop MCP server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/servers/{server_name}/restart", response_model=Dict[str, Any])
async def restart_mcp_server(
    server_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Restart an MCP server"""
    try:
        result = await mcp_server_manager.restart_server(server_name)
        return result
        
    except Exception as e:
        logger.error(f"Failed to restart MCP server: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/servers/{server_name}/health-check", response_model=Dict[str, Any])
async def health_check_mcp_server(
    server_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Perform health check on MCP server"""
    try:
        result = await mcp_server_manager.health_check_server(server_name)
        return result
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Tool management endpoints
@router.post("/servers/{server_name}/discover-tools", response_model=Dict[str, Any])
async def discover_mcp_tools(
    server_name: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Discover tools from an MCP server"""
    try:
        result = await mcp_tool_registry.discover_tools(
            db=db,
            server_name=server_name,
            organization_id=organization_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tools", response_model=List[Dict[str, Any]])
async def get_available_tools(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get available MCP tools"""
    try:
        tools = await mcp_tool_registry.get_available_tools(
            db=db,
            organization_id=organization_id,
            category=category,
            user_role=current_user.role
        )
        
        return tools
        
    except Exception as e:
        logger.error(f"Failed to get available tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available tools"
        )


@router.post("/tools/execute", response_model=Dict[str, Any])
async def execute_mcp_tool(
    execution_request: ToolExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Execute an MCP tool"""
    try:
        result = await mcp_tool_registry.execute_tool(
            db=db,
            tool_id=execution_request.tool_id,
            organization_id=organization_id,
            input_parameters=execution_request.input_parameters,
            user_id=str(current_user.id),
            conversation_id=execution_request.conversation_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/tools/approve", response_model=Dict[str, Any])
async def approve_tool_execution(
    approval_request: ToolApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Approve a pending tool execution"""
    try:
        # Check if user has approval permissions
        if not current_user.role or current_user.role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve tool executions"
            )
        
        result = await mcp_tool_registry.approve_tool_execution(
            db=db,
            execution_id=approval_request.execution_id,
            organization_id=organization_id,
            approver_id=str(current_user.id),
            approval_reason=approval_request.approval_reason
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool approval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tools/executions/{execution_id}", response_model=Dict[str, Any])
async def get_tool_execution_status(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get tool execution status"""
    try:
        status = await mcp_tool_registry.get_tool_execution_status(
            db=db,
            execution_id=execution_id,
            organization_id=organization_id
        )
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get execution status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Integration endpoints
@router.get("/integrations", response_model=Dict[str, Any])
async def get_available_integrations():
    """Get available third-party integrations"""
    try:
        integrations = await mcp_integration_manager.get_available_integrations()
        return integrations
        
    except Exception as e:
        logger.error(f"Failed to get integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available integrations"
        )


@router.post("/integrations/setup", response_model=Dict[str, Any])
async def setup_integration(
    setup_request: IntegrationSetupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Set up a third-party integration"""
    try:
        # Check if user has admin permissions
        if not current_user.role or current_user.role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required to set up integrations"
            )
        
        result = await mcp_integration_manager.setup_integration(
            db=db,
            organization_id=organization_id,
            integration_name=setup_request.integration_name,
            config=setup_request.config
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Integration setup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/integrations/{integration_name}/test", response_model=Dict[str, Any])
async def test_integration(
    integration_name: str,
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Test an integration configuration"""
    try:
        result = await mcp_integration_manager.test_integration(
            integration_name=integration_name,
            config=config
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Analytics and monitoring endpoints
@router.get("/analytics/tools", response_model=Dict[str, Any])
async def get_tool_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get tool usage analytics"""
    try:
        from datetime import datetime, timedelta
        from ..models.user import MCPToolExecution, MCPTool
        from sqlalchemy import func
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get tool executions
        executions = db.query(MCPToolExecution).filter(
            MCPToolExecution.organization_id == organization_id,
            MCPToolExecution.started_at >= start_date,
            MCPToolExecution.started_at <= end_date
        ).all()
        
        # Calculate metrics
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "completed"])
        failed_executions = len([e for e in executions if e.status == "failed"])
        pending_executions = len([e for e in executions if e.status in ["pending", "pending_approval"]])
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Tool usage breakdown
        tool_usage = {}
        for execution in executions:
            tool = db.query(MCPTool).filter(MCPTool.id == execution.tool_id).first()
            tool_name = tool.name if tool else "Unknown"
            
            if tool_name not in tool_usage:
                tool_usage[tool_name] = {"count": 0, "success": 0, "failed": 0}
            
            tool_usage[tool_name]["count"] += 1
            if execution.status == "completed":
                tool_usage[tool_name]["success"] += 1
            elif execution.status == "failed":
                tool_usage[tool_name]["failed"] += 1
        
        # Average execution time
        completed_executions = [e for e in executions if e.execution_time_ms]
        avg_execution_time = sum(e.execution_time_ms for e in completed_executions) / len(completed_executions) if completed_executions else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "totals": {
                "executions": total_executions,
                "successful": successful_executions,
                "failed": failed_executions,
                "pending": pending_executions
            },
            "metrics": {
                "success_rate": round(success_rate, 2),
                "average_execution_time_ms": round(avg_execution_time, 2)
            },
            "tool_usage": tool_usage
        }
        
    except Exception as e:
        logger.error(f"Failed to get tool analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics"
        )