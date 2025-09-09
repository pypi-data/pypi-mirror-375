# Powerset Agents Core

A factory system for creating specialized HEAVEN framework agents that systematically learn libraries through structured curricula.

## Overview

Powerset Agents Core provides a standardized factory for creating library learning agents. Each agent is configured with specific learning curricula, equipped with necessary MCPs and tools, and guided by generated system prompts to learn target libraries systematically.

**Key Concept**: Create agents that learn libraries through PayloadDiscovery sequences, track progress in STARLOG sessions, and use hands-on tools to explore and master specific libraries.

## Core Library Features

### 🏭 Factory System
- **`create_library_powerset_agent()`**: Main factory function for creating learning agents
- **Configuration Models**: Structured Pydantic models for agent configuration
- **HEAVEN Integration**: Converts configs to `HeavenAgentConfig` for framework compatibility
- **Dynamic System Prompts**: Generates contextual prompts based on target library and curriculum

### ⚙️ Agent Configuration
- **LibraryPowersetAgentConfig**: Core configuration with library path, help command, learning sequence
- **PayloadDiscoveryConfig**: Curriculum configuration with path/model and usage instructions
- **BasePowersetAgentConfig**: Base config with MCP servers, tools, session paths, and model settings

### 🔧 MCP Server Setup
- **STARLOG MCP**: Automatic configuration for session tracking and progress management
- **Waypoint MCP**: Automatic configuration for curriculum navigation and waypoint traversal
- **Environment Management**: Proper environment variable handling for MCP server startup

### 🛠️ Tool Integration
- **NetworkEditTool**: File operations for reading, writing, and editing during learning
- **BashTool**: Command execution for testing code and exploring library functionality
- **Tool Resolution**: Maps tool names to actual tool classes automatically

## Specialized Agent Implementations

### 🎯 MetaStack Powerset Agent
- **Target Library**: `pydantic_stack_core`
- **Specialization**: Building Pydantic model systems that generate structured string outputs
- **Use Case**: Creating composable, renderable model architectures

### 📚 PayloadDiscovery Powerset Agent  
- **Target Library**: `payload_discovery`
- **Specialization**: Building learning curricula and prompt injection sequences
- **Use Case**: Creating systematic learning materials for other agents

## Installation

[Installation instructions pending PyPI publication]

## Quick Start

```python
from powerset_agents_core import create_library_powerset_agent
from payload_discovery.core import load_payload_discovery

# Load learning sequence
pd = load_payload_discovery("/path/to/learning_sequence.json")

# Create agent configuration
agent_config = create_library_powerset_agent(
    pkg_path="pydantic_stack_core",
    help_command="python -c 'import pydantic_stack_core; help(pydantic_stack_core)'",
    payload_discovery=pd,
    name="MetaStackLearningAgent",
    starlog_path="/tmp/metastack_learning_session",
    description="Agent that learns the MetaStack library"
)

# Use with HEAVEN framework to create actual agent
# (Implementation depends on HEAVEN framework integration)
```

## Architecture

### BasePowersetAgentConfig
Base configuration for all powerset agents with:
- Agent identity (name, description) 
- HEAVEN configuration (model, max_iterations)
- Session paths (starlog_path, workspace_path)
- Standard MCP servers (waypoint, starlog)
- Standard tools (networkedittool, bashtool)

### LibraryPowersetAgentConfig  
Extends BasePowersetAgentConfig for library learning with:
- Target library (pkg_path, help_command)
- Learning sequence (PayloadDiscovery)

### Factory Function
`create_library_powerset_agent()` converts LibraryPowersetAgentConfig to HeavenAgentConfig with:
- Configured MCP servers and tools
- Generated system prompt for library learning
- Library-specific configuration embedded

## Agent Behavior

1. **Initialize**: Start STARLOG session for learning tracking
2. **Navigate**: Use Waypoint MCP to follow PayloadDiscovery sequence  
3. **Introspect**: Use help_command to explore the target library
4. **Explore**: Use NetworkEditTool and BashTool for hands-on learning
5. **Document**: Create examples, tests, and documentation
6. **Log**: Track discoveries and insights in STARLOG
7. **Improve**: Generate new learning materials for future sessions

## Dependencies

- `heaven-framework`: BaseHeavenAgent and core framework
- `starlog-mcp`: Session tracking and progress logging
- `payload-discovery`: Structured learning sequences and Waypoint MCP
- `pydantic>=2.0.0`: Configuration models

## License

MIT License