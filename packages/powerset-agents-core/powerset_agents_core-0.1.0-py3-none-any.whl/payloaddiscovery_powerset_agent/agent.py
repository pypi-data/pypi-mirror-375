"""PayloadDiscovery Powerset Agent creation."""

import os
from powerset_agents_core.factory import create_library_powerset_agent
from powerset_agents_core.config import PayloadDiscoveryConfig


def create_payloaddiscovery_agent(starlog_path: str = "/tmp/payloaddiscovery_agent_starlog") -> "HeavenAgentConfig":
    """
    Create a PayloadDiscovery powerset agent that can learn and use payload_discovery.
    
    This agent can create any prompt injection sequence for waypoint.
    
    Args:
        starlog_path: Path for agent's STARLOG session tracking
        
    Returns:
        HeavenAgentConfig ready to be used with HEAVEN framework
        
    Example:
        >>> agent_config = create_payloaddiscovery_agent()
        >>> # Use with HEAVEN framework to run the agent
    """
    
    # Create the PayloadDiscovery config for learning PayloadDiscovery
    pd_config = PayloadDiscoveryConfig(
        path="/tmp/understand_powerset_library.json",  # Generic library learning PD
        instructions="Learn payload_discovery library to build prompt injection sequences and learning curricula"
    )
    
    # Create the agent using the factory
    agent_config = create_library_powerset_agent(
        pkg_path="payload_discovery",
        help_command="python -c 'import payload_discovery; help(payload_discovery)'",
        payload_discovery_config=pd_config,
        name="PayloadDiscoveryPowersetAgent", 
        starlog_path=starlog_path,
        description="Specialized agent for learning payload_discovery and building learning curricula",
        workspace_path="/tmp"
    )
    
    return agent_config