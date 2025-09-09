"""Configuration models for Powerset Agents."""

from typing import Optional, List
from pydantic import BaseModel, Field
from payload_discovery.core import PayloadDiscovery


class PayloadDiscoveryConfig(BaseModel):
    """Configuration for PayloadDiscovery curriculum."""
    path: Optional[str] = Field(None, description="Path to the PayloadDiscovery JSON file")
    model: Optional[PayloadDiscovery] = Field(None, description="PayloadDiscovery model instance")
    instructions: str = Field(..., description="When/how to use this curriculum")
    
    class Config:
        arbitrary_types_allowed = True


class BasePowersetAgentConfig(BaseModel):
    """Base configuration for all powerset agents."""
    
    # Agent identity
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(None, description="Description of what this agent does")
    
    # HEAVEN agent configuration
    model: str = Field(default="gpt-5-mini", description="LLM model to use")
    max_iterations: int = Field(default=50, description="Maximum agent iterations")
    
    # Session configuration
    starlog_path: str = Field(..., description="Path for STARLOG session tracking")
    workspace_path: str = Field(default="/tmp", description="Workspace directory for agent operations")
    
    # MCP configuration (common to all powerset agents)
    mcp_servers: List[str] = Field(default=["waypoint", "starlog"], description="MCP servers to equip")
    tools: List[str] = Field(default=["networkedittool", "bashtool"], description="Tools to equip")
    
    # System prompt override
    custom_system_prompt: Optional[str] = Field(None, description="Custom system prompt (overrides default)")


class LibraryPowersetAgentConfig(BasePowersetAgentConfig):
    """Configuration for library learning powerset agents."""
    
    # Target library to learn
    pkg_path: str = Field(..., description="Path or name of the library package to learn")
    help_command: str = Field(..., description="Command to introspect the library (e.g., 'python -c \"import pkg; help(pkg)\"')")
    
    # Learning sequence
    payload_discovery_config: PayloadDiscoveryConfig = Field(..., description="PayloadDiscovery configuration for this library")