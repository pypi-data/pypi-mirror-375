#!/usr/bin/env python3
"""
MetaStack Powerset Agent CLI

This creates a CLI for the MetaStack powerset agent that can learn pydantic_stack_core
and generate any Pydantic model system that produces string output.

Usage:
1. Start the HEAVEN HTTP server: python /home/GOD/core/image/http_server.py
2. Run this script: python -m metastack_powerset_agent.cli
"""

# No sys.path manipulation - use installed packages only

from heaven_base.cli import make_cli
from .agent import create_metastack_agent


def main():
    """Create and run MetaStack powerset agent CLI."""
    print("🌟 Initializing MetaStack Powerset Agent...")
    
    # Create the agent config
    agent_config = create_metastack_agent()
    
    # Create CLI instance
    cli = make_cli(
        agent_config=agent_config,
        server_url="http://localhost:8080"
    )
    
    print("✅ MetaStack Agent ready!")
    print("💡 This agent can learn pydantic_stack_core and build Pydantic models that generate string outputs")
    
    # Run the CLI
    cli.run_sync()


if __name__ == "__main__":
    main()