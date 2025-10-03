#!/usr/bin/env python3
"""
MCP Client for Deep Research Agent
Allows other applications to interact with the research server
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-client")

class DeepResearchMCPClient:
    """Client wrapper for Deep Research Agent MCP server"""

    def __init__(self, server_path: str = "mcp_server.py"):
        self.server_path = server_path
        self.session = None
        self.session_manager = None

    async def connect(self):
        """Connect to the MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path],
            )

            # Fix: Use proper async context manager
            self.session_manager = stdio_client(server_params)
            self.session = await self.session_manager.__aenter__()
            await self.session.initialize()
            logger.info("Connected to Deep Research MCP server")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session_manager:
            try:
                await self.session_manager.__aexit__(None, None, None)
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.session = None
                self.session_manager = None

    async def research(self, query: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None, max_sources: int = 5) -> str:
        """Perform comprehensive research on a topic"""
        if not self.session:
            await self.connect()

        try:
            args = {
                "query": query,
                "max_sources": max_sources
            }

            if start_date:
                args["start_date"] = start_date
            if end_date:
                args["end_date"] = end_date

            result = await self.session.call_tool("deep_research", args)

            if result and result.content:
                return result.content[0].text if result.content[0].text else "No results"
            return "No results returned"

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return f"Research failed: {str(e)}"

    async def get_capabilities(self) -> str:
        """Get server capabilities"""
        if not self.session:
            await self.connect()

        try:
            result = await self.session.read_resource("research://capabilities")
            return result.contents[0].text if result.contents else "No capabilities found"
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            return f"Failed to get capabilities: {str(e)}"

# Example usage functions
async def example_research():
    """Example of how to use the MCP client"""
    client = DeepResearchMCPClient()

    try:
        await client.connect()

        # Get capabilities
        print("=== Server Capabilities ===")
        capabilities = await client.get_capabilities()
        print(capabilities)

        # Perform research
        print("\n=== Research Example ===")
        query = "AI trends in 2024"
        result = await client.research(
            query=query,
            start_date="2024-01-01",
            end_date="2024-12-31",
            max_sources=3
        )
        print(result)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(example_research())
