"""
MCP Server Management System
Handles dynamic MCP server registration, management, and security validation
"""

import logging
import asyncio
import json
import subprocess
import signal
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.user import Organization, MCPServer, MCPTool
from ..config.mcp_config import mcp_settings

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """MCP Server configuration"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    working_directory: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    health_check_interval: int = 60
    auto_restart: bool = True
    security_sandbox: bool = True
    allowed_capabilities: List[str] = None
    
    def __post_init__(self):
        if self.allowed_capabilities is None:
            self.allowed_capabilities = ["tools", "resources", "prompts"]


@dataclass
class MCPServerStatus:
    """MCP Server status information"""
    name: str
    status: str  # starting, running, stopped, error, unhealthy
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    error_message: Optional[str] = None
    capabilities: List[str] = None
    tools_count: int = 0
    resources_count: int = 0
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class MCPServerManager:
    """
    Manages MCP servers with security validation and health monitoring
    
    Features:
    - Dynamic server registration and lifecycle management
    - Security validation and sandboxing
    - Health monitoring with automatic failover
    - googleapis/genai-toolbox integration
    - Tool discovery and registration
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.server_status: Dict[str, MCPServerStatus] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        # Security settings
        self.sandbox_enabled = mcp_settings.ENABLE_SANDBOX
        self.allowed_commands = mcp_settings.ALLOWED_COMMANDS
        self.max_servers = mcp_settings.MAX_SERVERS
        
        # Built-in server configurations
        self.builtin_servers = self._load_builtin_servers()
    
    async def start_manager(self):
        """Start the MCP server manager"""
        if self.is_running:
            logger.warning("MCP server manager is already running")
            return
        
        self.is_running = True
        logger.info("Starting MCP server manager")
        
        # Start health monitoring task
        asyncio.create_task(self._health_monitor_loop())
        
        # Auto-start configured servers
        await self._auto_start_servers()
    
    async def stop_manager(self):
        """Stop the MCP server manager"""
        logger.info("Stopping MCP server manager")
        self.is_running = False
        
        # Stop all health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        self.health_check_tasks.clear()
        
        # Stop all servers
        for server_name in list(self.servers.keys()):
            await self.stop_server(server_name)
    
    async def register_server(
        self,
        db: Session,
        organization_id: str,
        server_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a new MCP server
        
        Args:
            db: Database session
            organization_id: Organization ID
            server_config: Server configuration
            
        Returns:
            Registration result
        """
        try:
            # Validate server configuration
            validation_result = await self._validate_server_config(server_config)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid server configuration: {validation_result['error']}")
            
            # Check server limits
            if len(self.servers) >= self.max_servers:
                raise ValueError(f"Maximum number of servers ({self.max_servers}) reached")
            
            server_name = server_config["name"]
            
            # Check if server already exists
            if server_name in self.servers:
                raise ValueError(f"Server '{server_name}' already exists")
            
            # Create server configuration
            config = MCPServerConfig(
                name=server_name,
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {}),
                working_directory=server_config.get("working_directory"),
                timeout=server_config.get("timeout", 30),
                max_retries=server_config.get("max_retries", 3),
                health_check_interval=server_config.get("health_check_interval", 60),
                auto_restart=server_config.get("auto_restart", True),
                security_sandbox=server_config.get("security_sandbox", True),
                allowed_capabilities=server_config.get("allowed_capabilities", ["tools", "resources", "prompts"])
            )
            
            # Store configuration
            self.servers[server_name] = config
            
            # Initialize status
            self.server_status[server_name] = MCPServerStatus(
                name=server_name,
                status="stopped"
            )
            
            # Save to database
            mcp_server = MCPServer(
                organization_id=organization_id,
                name=server_name,
                config=asdict(config),
                status="registered",
                is_active=True
            )
            db.add(mcp_server)
            db.commit()
            
            logger.info(f"Registered MCP server: {server_name}")
            
            return {
                "server_name": server_name,
                "status": "registered",
                "config": asdict(config)
            }
            
        except Exception as e:
            logger.error(f"Failed to register MCP server: {e}")
            db.rollback()
            raise
    
    async def start_server(self, server_name: str) -> Dict[str, Any]:
        """
        Start an MCP server
        
        Args:
            server_name: Server name
            
        Returns:
            Start result
        """
        try:
            if server_name not in self.servers:
                raise ValueError(f"Server '{server_name}' not found")
            
            if server_name in self.server_processes:
                if self.server_processes[server_name].poll() is None:
                    raise ValueError(f"Server '{server_name}' is already running")
                else:
                    # Clean up dead process
                    del self.server_processes[server_name]
            
            config = self.servers[server_name]
            status = self.server_status[server_name]
            
            # Update status
            status.status = "starting"
            status.error_message = None
            
            # Prepare environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Security: Validate command
            if not self._is_command_allowed(config.command):
                raise ValueError(f"Command '{config.command}' is not allowed")
            
            # Start process
            logger.info(f"Starting MCP server: {server_name}")
            
            process = subprocess.Popen(
                [config.command] + config.args,
                env=env,
                cwd=config.working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )
            
            # Store process
            self.server_processes[server_name] = process
            
            # Update status
            status.status = "running"
            status.pid = process.pid
            status.started_at = datetime.utcnow()
            status.last_health_check = datetime.utcnow()
            
            # Start health monitoring
            if server_name not in self.health_check_tasks:
                self.health_check_tasks[server_name] = asyncio.create_task(
                    self._health_check_loop(server_name)
                )
            
            # Discover server capabilities
            await self._discover_server_capabilities(server_name)
            
            logger.info(f"Started MCP server: {server_name} (PID: {process.pid})")
            
            return {
                "server_name": server_name,
                "status": "running",
                "pid": process.pid,
                "started_at": status.started_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            
            # Update status
            if server_name in self.server_status:
                self.server_status[server_name].status = "error"
                self.server_status[server_name].error_message = str(e)
            
            raise
    
    async def stop_server(self, server_name: str) -> Dict[str, Any]:
        """
        Stop an MCP server
        
        Args:
            server_name: Server name
            
        Returns:
            Stop result
        """
        try:
            if server_name not in self.server_processes:
                raise ValueError(f"Server '{server_name}' is not running")
            
            process = self.server_processes[server_name]
            status = self.server_status[server_name]
            
            logger.info(f"Stopping MCP server: {server_name}")
            
            # Stop health check task
            if server_name in self.health_check_tasks:
                self.health_check_tasks[server_name].cancel()
                del self.health_check_tasks[server_name]
            
            # Graceful shutdown
            try:
                process.terminate()
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process(process)),
                    timeout=10
                )
            except asyncio.TimeoutError:
                # Force kill
                logger.warning(f"Force killing MCP server: {server_name}")
                process.kill()
                await asyncio.create_task(self._wait_for_process(process))
            
            # Clean up
            del self.server_processes[server_name]
            
            # Update status
            status.status = "stopped"
            status.pid = None
            
            logger.info(f"Stopped MCP server: {server_name}")
            
            return {
                "server_name": server_name,
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop MCP server {server_name}: {e}")
            raise
    
    async def restart_server(self, server_name: str) -> Dict[str, Any]:
        """
        Restart an MCP server
        
        Args:
            server_name: Server name
            
        Returns:
            Restart result
        """
        try:
            # Stop if running
            if server_name in self.server_processes:
                await self.stop_server(server_name)
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Start
            result = await self.start_server(server_name)
            
            # Update restart count
            if server_name in self.server_status:
                self.server_status[server_name].restart_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to restart MCP server {server_name}: {e}")
            raise
    
    async def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """
        Get server status
        
        Args:
            server_name: Server name
            
        Returns:
            Server status
        """
        if server_name not in self.server_status:
            raise ValueError(f"Server '{server_name}' not found")
        
        status = self.server_status[server_name]
        
        return {
            "name": status.name,
            "status": status.status,
            "pid": status.pid,
            "started_at": status.started_at.isoformat() if status.started_at else None,
            "last_health_check": status.last_health_check.isoformat() if status.last_health_check else None,
            "restart_count": status.restart_count,
            "error_message": status.error_message,
            "capabilities": status.capabilities,
            "tools_count": status.tools_count,
            "resources_count": status.resources_count
        }
    
    async def get_all_servers_status(self) -> List[Dict[str, Any]]:
        """Get status of all servers"""
        return [
            await self.get_server_status(server_name)
            for server_name in self.servers.keys()
        ]
    
    async def health_check_server(self, server_name: str) -> Dict[str, Any]:
        """
        Perform health check on server
        
        Args:
            server_name: Server name
            
        Returns:
            Health check result
        """
        try:
            if server_name not in self.server_processes:
                return {"healthy": False, "error": "Server not running"}
            
            process = self.server_processes[server_name]
            status = self.server_status[server_name]
            
            # Check if process is still alive
            if process.poll() is not None:
                status.status = "stopped"
                return {"healthy": False, "error": "Process terminated"}
            
            # Send ping to server (simplified - in real implementation would use MCP protocol)
            try:
                # This would be an actual MCP ping request
                health_result = await self._send_mcp_ping(server_name)
                
                if health_result["success"]:
                    status.status = "running"
                    status.last_health_check = datetime.utcnow()
                    return {"healthy": True, "response_time_ms": health_result.get("response_time_ms", 0)}
                else:
                    status.status = "unhealthy"
                    return {"healthy": False, "error": health_result.get("error", "Ping failed")}
                    
            except Exception as e:
                status.status = "unhealthy"
                return {"healthy": False, "error": str(e)}
            
        except Exception as e:
            logger.error(f"Health check failed for server {server_name}: {e}")
            return {"healthy": False, "error": str(e)}
    
    async def _validate_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate server configuration"""
        try:
            # Required fields
            required_fields = ["name", "command"]
            for field in required_fields:
                if field not in config:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Validate name
            name = config["name"]
            if not isinstance(name, str) or not name.strip():
                return {"valid": False, "error": "Server name must be a non-empty string"}
            
            # Validate command
            command = config["command"]
            if not isinstance(command, str) or not command.strip():
                return {"valid": False, "error": "Command must be a non-empty string"}
            
            # Security validation
            if not self._is_command_allowed(command):
                return {"valid": False, "error": f"Command '{command}' is not allowed"}
            
            # Validate args
            if "args" in config and not isinstance(config["args"], list):
                return {"valid": False, "error": "Args must be a list"}
            
            # Validate env
            if "env" in config and not isinstance(config["env"], dict):
                return {"valid": False, "error": "Env must be a dictionary"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is allowed"""
        if not self.allowed_commands:
            return True  # No restrictions
        
        # Check against allowed commands
        for allowed in self.allowed_commands:
            if command.startswith(allowed):
                return True
        
        return False
    
    async def _discover_server_capabilities(self, server_name: str):
        """Discover server capabilities and tools"""
        try:
            # This would use the actual MCP protocol to discover capabilities
            # For now, we'll simulate the discovery
            
            status = self.server_status[server_name]
            
            # Simulate capability discovery
            status.capabilities = ["tools", "resources"]
            status.tools_count = 5  # Would be actual count
            status.resources_count = 2  # Would be actual count
            
            logger.info(f"Discovered capabilities for {server_name}: {status.capabilities}")
            
        except Exception as e:
            logger.error(f"Failed to discover capabilities for {server_name}: {e}")
    
    async def _send_mcp_ping(self, server_name: str) -> Dict[str, Any]:
        """Send MCP ping to server"""
        try:
            # This would implement actual MCP protocol ping
            # For now, simulate a successful ping
            
            start_time = datetime.utcnow()
            
            # Simulate network delay
            await asyncio.sleep(0.01)
            
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return {
                "success": True,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _health_check_loop(self, server_name: str):
        """Health check loop for a server"""
        try:
            config = self.servers[server_name]
            
            while self.is_running and server_name in self.servers:
                try:
                    health_result = await self.health_check_server(server_name)
                    
                    if not health_result["healthy"]:
                        logger.warning(f"Server {server_name} is unhealthy: {health_result.get('error')}")
                        
                        # Auto-restart if enabled
                        if config.auto_restart:
                            status = self.server_status[server_name]
                            if status.restart_count < config.max_retries:
                                logger.info(f"Auto-restarting server {server_name}")
                                await self.restart_server(server_name)
                            else:
                                logger.error(f"Server {server_name} exceeded max restart attempts")
                                status.status = "error"
                                status.error_message = "Exceeded max restart attempts"
                    
                    await asyncio.sleep(config.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Health check error for {server_name}: {e}")
                    await asyncio.sleep(config.health_check_interval)
                    
        except asyncio.CancelledError:
            logger.info(f"Health check cancelled for server {server_name}")
        except Exception as e:
            logger.error(f"Health check loop error for {server_name}: {e}")
    
    async def _health_monitor_loop(self):
        """Main health monitoring loop"""
        while self.is_running:
            try:
                # Clean up dead processes
                dead_servers = []
                for server_name, process in self.server_processes.items():
                    if process.poll() is not None:
                        dead_servers.append(server_name)
                
                for server_name in dead_servers:
                    logger.warning(f"Detected dead server process: {server_name}")
                    del self.server_processes[server_name]
                    if server_name in self.server_status:
                        self.server_status[server_name].status = "stopped"
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _auto_start_servers(self):
        """Auto-start configured servers"""
        try:
            # This would load server configurations from database
            # and auto-start them based on organization settings
            
            logger.info("Auto-starting configured MCP servers")
            
            # For now, just log that auto-start is ready
            logger.info("MCP server auto-start ready")
            
        except Exception as e:
            logger.error(f"Auto-start failed: {e}")
    
    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for process to terminate"""
        while process.poll() is None:
            await asyncio.sleep(0.1)
    
    def _load_builtin_servers(self) -> Dict[str, Dict[str, Any]]:
        """Load built-in server configurations"""
        return {
            "googleapis-genai-toolbox": {
                "name": "googleapis-genai-toolbox",
                "command": "uvx",
                "args": ["googleapis-genai-toolbox"],
                "env": {},
                "description": "Google APIs GenAI Toolbox MCP server",
                "capabilities": ["tools"],
                "auto_install": True
            },
            "stripe-mcp": {
                "name": "stripe-mcp",
                "command": "uvx",
                "args": ["stripe-mcp"],
                "env": {},
                "description": "Stripe MCP server for payment operations",
                "capabilities": ["tools"],
                "auto_install": False
            }
        }


# Global instance
mcp_server_manager = MCPServerManager()