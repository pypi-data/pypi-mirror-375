"""MetaStack Powerset Agent creation."""

import os
from powerset_agents_core.factory import create_library_powerset_agent
from powerset_agents_core.config import PayloadDiscoveryConfig


def create_metastack_agent(starlog_path: str = "/tmp/metastack_agent_starlog") -> "HeavenAgentConfig":
    """
    Create a MetaStack powerset agent that can learn and use pydantic_stack_core.
    
    This agent can generate any Pydantic model system that produces string output.
    
    Args:
        starlog_path: Path for agent's STARLOG session tracking
        
    Returns:
        HeavenAgentConfig ready to be used with HEAVEN framework
        
    Example:
        >>> agent_config = create_metastack_agent()
        >>> # Use with HEAVEN framework to run the agent
    """
    
    # Create the PayloadDiscovery config for learning MetaStack
    pd_config = PayloadDiscoveryConfig(
        path="/tmp/understand_powerset_library.json",  # Generic library learning PD
        instructions="Learn pydantic_stack_core library to build Pydantic models that generate string outputs"
    )
    
    # Create the agent using the factory
    agent_config = create_library_powerset_agent(
        pkg_path="pydantic_stack_core",
        help_command="python -c 'import pydantic_stack_core; help(pydantic_stack_core)'",
        payload_discovery_config=pd_config,
        name="MetaStackPowersetAgent",
        starlog_path=starlog_path,
        description="Specialized agent for learning pydantic_stack_core and building Pydantic model systems",
        workspace_path="/tmp"
    )
    
    return agent_config