"""
Powerset Agents Core - Factory for self-improving BaseHeavenAgent instances.

Creates standardized agents that learn libraries through PayloadDiscovery sequences,
using STARLOG for session tracking and Waypoint MCP for navigation.
"""

from .factory import create_library_powerset_agent
from .config import BasePowersetAgentConfig, LibraryPowersetAgentConfig, PayloadDiscoveryConfig

__version__ = "0.1.0"

__all__ = [
    "create_library_powerset_agent",
    "BasePowersetAgentConfig", 
    "LibraryPowersetAgentConfig",
    "PayloadDiscoveryConfig"
]