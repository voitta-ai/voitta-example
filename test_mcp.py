#!/usr/bin/env python3
"""
Test script for the MCP integration in Voitta.
This script tests the MCP integration by initializing the VoittaRouter with MCP configuration
and discovering MCP tools.
"""

import asyncio
import yaml
import json
import os
from voitta import VoittaRouter, MCPServerDescription


async def test_mcp_integration():
    """Test the MCP integration by discovering tools and printing them."""
    print("Loading configuration...")

    # Initialize the router with the configuration file
    voittaRouter = VoittaRouter("voitta.yaml")

    # Discover MCP tools
    print("Discovering MCP tools...")
    try:
        await voittaRouter.discover_mcp_tools()
        print("MCP tool discovery completed successfully")
    except Exception as e:
        print(f"Error during MCP tool discovery: {e}")
        return

    # Get tools and prompt
    tools = voittaRouter.get_tools()
    tool_prompt = voittaRouter.get_prompt()

    # Print MCP tools
    mcp_tools = [tool for tool in tools if tool["function"]
                 ["name"].startswith("mcp")]
    print(f"Found {len(mcp_tools)} MCP tools:")
    for tool in mcp_tools:
        print(
            f"  - {tool['function']['name']}: {tool['function']['description']}")

    # Print tool prompt
    print("\nTool prompt:")
    print(tool_prompt)

    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
