"""Factory function for creating Powerset Agents."""

import logging
from typing import Optional, List, Dict, Any
from payload_discovery.core import PayloadDiscovery
from heaven_base.baseheavenagent import HeavenAgentConfig
from heaven_base.unified_chat import ProviderEnum
from heaven_base.tools.network_edit_tool import NetworkEditTool
from heaven_base.tools.bash_tool import BashTool
from .config import LibraryPowersetAgentConfig, PayloadDiscoveryConfig

logger = logging.getLogger(__name__)


def create_library_powerset_agent(
    pkg_path: str,
    help_command: str, 
    payload_discovery_config: PayloadDiscoveryConfig,
    name: str,
    starlog_path: str,
    description: Optional[str] = None,
    workspace_path: str = "/tmp",
    model: str = "gpt-5-mini",
    max_iterations: int = 50,
    custom_system_prompt: Optional[str] = None
) -> HeavenAgentConfig:
    """
    Create a HeavenAgentConfig for learning a specific library.
    
    Args:
        pkg_path: Path or name of the library package to learn
        help_command: Command to introspect the library (e.g., 'python -c "import pkg; help(pkg)"')
        payload_discovery_config: PayloadDiscovery configuration (path or model + instructions)
        name: Name of the agent
        starlog_path: Path for STARLOG session tracking
        description: Optional description of what this agent learns
        workspace_path: Workspace directory for agent operations
        model: LLM model to use
        max_iterations: Maximum learning iterations
        custom_system_prompt: Custom system prompt (overrides default)
        
    Returns:
        HeavenAgentConfig configured for library learning with waypoint/starlog MCPs and tools
        
    Example:
        >>> from payload_discovery.core import load_payload_discovery
        >>> pd = load_payload_discovery("/path/to/metastack_learning.json")
        >>> agent_config = create_library_powerset_agent(
        ...     pkg_path="pydantic_stack_core",
        ...     help_command="python -c 'import pydantic_stack_core; help(pydantic_stack_core)'",
        ...     payload_discovery=pd,
        ...     name="MetaStackLearningAgent",
        ...     starlog_path="/tmp/metastack_learning_session"
        ... )
        >>> # Use with HEAVEN framework to create actual agent
    """
    logger.info(f"Creating Library Powerset Agent config: {name} for package: {pkg_path}")
    logger.debug(f"Agent config - model: {model}, max_iterations: {max_iterations}, workspace: {workspace_path}")
    
    config = LibraryPowersetAgentConfig(
        pkg_path=pkg_path,
        help_command=help_command,
        payload_discovery_config=payload_discovery_config,
        name=name,
        starlog_path=starlog_path,
        description=description,
        workspace_path=workspace_path,
        model=model,
        max_iterations=max_iterations,
        custom_system_prompt=custom_system_prompt
    )
    
    # Convert to HeavenAgentConfig
    heaven_config = _convert_to_heaven_config(config)
    logger.info(f"Successfully created HeavenAgentConfig for: {name}")
    
    return heaven_config


def _convert_to_heaven_config(config: LibraryPowersetAgentConfig) -> HeavenAgentConfig:
    """Convert LibraryPowersetAgentConfig to HeavenAgentConfig."""
    logger.info(f"Converting {config.name} to HeavenAgentConfig")
    
    system_prompt = config.custom_system_prompt or _generate_library_learning_prompt(config)
    provider = _get_provider_for_model(config.model)
    tools = _resolve_tool_classes(config.tools)
    mcp_servers = _get_default_mcp_servers()
    
    return HeavenAgentConfig(
        name=config.name,
        system_prompt=system_prompt,
        tools=tools,
        provider=provider,
        model=config.model,
        mcp_servers=mcp_servers
    )


def _get_default_mcp_servers() -> Dict[str, Dict[str, Any]]:
    """Get default MCP server configurations for powerset agents."""
    return {
        "starlog": {
            "transport": "stdio", 
            "command": "python",
            "args": ["-m", "starlog_mcp.starlog_mcp"],
            "env": {"HEAVEN_DATA_DIR": "/tmp/heaven_data"}
        },
        "waypoint": {
            "transport": "stdio",
            "command": "python", 
            "args": ["-m", "payload_discovery.mcp_server_v2"]
        }
    }


def _resolve_tool_classes(tool_names: List[str]) -> List:
    """Resolve tool names to actual tool classes."""
    tool_mapping = {
        "networkedittool": NetworkEditTool,
        "bashtool": BashTool
    }
    
    tools = []
    for tool_name in tool_names:
        tool_class = tool_mapping.get(tool_name.lower())
        if tool_class:
            tools.append(tool_class)
        else:
            logger.warning(f"Unknown tool: {tool_name}")
    
    return tools


def _build_mcp_servers(config: LibraryPowersetAgentConfig) -> Dict[str, Dict[str, Any]]:
    """Build MCP server configurations for the agent."""
    mcp_configs = {}
    
    if "waypoint" in config.mcp_servers:
        mcp_configs["waypoint"] = {
            "command": "python",
            "args": ["-m", "payload_discovery.mcp_server"],
            # "env": {"PYTHONPATH": "/home/GOD"}
        }
    
    if "starlog" in config.mcp_servers:
        mcp_configs["starlog"] = {
            "command": "python",
            "args": ["-m", "starlog_mcp.server"],
            # "env": {"PYTHONPATH": "/home/GOD"}
        }
    
    return mcp_configs


def _get_provider_for_model(model: str) -> ProviderEnum:
    """Map model name to provider enum."""
    model_lower = model.lower()
    
    if "gpt" in model_lower:
        return ProviderEnum.OPENAI
    elif "claude" in model_lower:
        return ProviderEnum.ANTHROPIC
    elif "gemini" in model_lower or "bison" in model_lower:
        return ProviderEnum.GOOGLE
    elif "llama" in model_lower or "mixtral" in model_lower:
        return ProviderEnum.GROQ
    elif "deepseek" in model_lower:
        return ProviderEnum.DEEPSEEK
    else:
        # Default to OpenAI for unknown models
        logger.warning(f"Unknown model {model}, defaulting to OpenAI provider")
        return ProviderEnum.OPENAI


def _generate_library_learning_prompt(config: LibraryPowersetAgentConfig) -> str:
    """Generate system prompt for library learning."""
    # Determine curriculum path
    if config.payload_discovery_config.path:
        curriculum_path = config.payload_discovery_config.path
    else:
        curriculum_path = "/tmp/generated_curriculum.json"  # Will need to save model to path
    
    return f"""You are {config.name}, a specialized library learning agent.

Your mission: Learn the {config.pkg_path} library and complete user requests. The `help command` for this library is: `{config.help_command}`.

CURRICULUM: {config.payload_discovery_config.instructions}

CAPABILITIES:
- STARLOG MCP: Session management and progress tracking
- Waypoint MCP: Navigate through structured learning sequences  
- NetworkEditTool: Read, write, and edit files
- BashTool: Run commands, test code, explore the library

CRITICAL DIRECTORY SEPARATION:
- WORKING DIRECTORY: Use current directory for all file operations (reading user files, writing code)
- STARLOG DIRECTORY: ALWAYS use "{config.starlog_path}" for ALL STARLOG commands

STARLOG PATH RULE: For ALL STARLOG commands, ALWAYS use path="{config.starlog_path}":
- fly("{config.starlog_path}")
- check("{config.starlog_path}")  
- start_starlog(..., path="{config.starlog_path}")
- update_debug_diary(..., path="{config.starlog_path}")
- add_rule(..., path="{config.starlog_path}")
- All other STARLOG commands

WORKFLOW:
1. Start session: Use fly("{config.starlog_path}") to initialize your STARLOG session journey
2. Learn library: Use waypoint with {curriculum_path}
3. Complete request: Follow user's request using your library knowledge (work in current directory)
4. Upload project: Use waypoint with /tmp/github_update_protocol.json to create and upload to GitHub

WORKSPACE: {config.workspace_path}

Your main workflow is to use starlog.fly("{config.starlog_path}") then follow instructions to begin the session. Once session is confirmed started by STARLOG, use the library learning PD in waypoint. Then, proceed as necessary to complete user request. Once you are done, use waypoint with github_update_protocol.

Begin by calling fly("{config.starlog_path}") to start your session."""