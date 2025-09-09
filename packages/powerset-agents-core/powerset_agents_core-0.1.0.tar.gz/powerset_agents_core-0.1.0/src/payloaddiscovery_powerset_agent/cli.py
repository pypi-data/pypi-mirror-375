#!/usr/bin/env python3
"""
PayloadDiscovery Powerset Agent CLI

This creates a CLI for the PayloadDiscovery powerset agent that can learn payload_discovery
and create any prompt injection sequence for waypoint.

Usage:
1. Start the HEAVEN HTTP server: python /home/GOD/core/image/http_server.py  
2. Run this script: python -m payloaddiscovery_powerset_agent.cli
"""

# No sys.path manipulation - use installed packages only

from heaven_base.cli import make_cli
from .agent import create_payloaddiscovery_agent


def main():
    """Create and run PayloadDiscovery powerset agent CLI."""
    print("🌟 Initializing PayloadDiscovery Powerset Agent...")
    
    # Create the agent config
    agent_config = create_payloaddiscovery_agent()
    
    # Create CLI instance
    cli = make_cli(
        agent_config=agent_config,
        server_url="http://localhost:8080"
    )
    
    print("✅ PayloadDiscovery Agent ready!")
    print("💡 This agent can learn payload_discovery and create prompt injection sequences for waypoint")
    
    # Run the CLI
    cli.run_sync()


if __name__ == "__main__":
    main()