#!/usr/bin/env python3
"""
MCP Server for Deep Research Agent
Provides research capabilities through Model Context Protocol
Using exact main.py logic with categorized summaries and fact check prompt
"""

import asyncio
import logging
import sys
import os
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from model import GGUFModel
    from scrapper import scrape_multiple_urls
    from social_media import RapidAIAgent
    from url_generator import generate_urls
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-mcp")

MODEL_PATH = r"C:\Users\jashp\Downloads\Deep Research Agent\mistral-7b-instruct-v0.2.Q4_K_S.gguf"
LLAMA_CLI_BIN = r"C:\Users\jashp\Downloads\Deep Research Agent\llama.cpp\build\bin\Release\llama-cli.exe"
RAPIDAI_API_KEY = "YOUR API"

model = None
rapid_agent = None

def categorize_scraped_data(urls, scraped_texts, rapidai_content=""):
    categorized = {}
    if rapidai_content.strip():
        categorized["RapidAI"] = [rapidai_content]
    for url, text in zip(urls, scraped_texts):
        if not text.strip():
            continue
        if "google.com/search" in url:
            source = "Google Search"
        elif "news.google.com" in url:
            source = "Google News"
        elif "wikipedia.org" in url:
            source = "Wikipedia"
        elif "reddit.com" in url:
            source = "Reddit"
        elif "medium.com" in url:
            source = "Medium"
        elif "bbc.com" in url or "cnn.com" in url:
            source = "News Site"
        else:
            source = "Other"
        categorized.setdefault(source, []).append(text)
    return categorized

def initialize_components():
    global model, rapid_agent
    try:
        model = GGUFModel(
            model_path=MODEL_PATH,
            llama_cli_path=LLAMA_CLI_BIN,
            threads=6,
            max_tokens=256,
            temperature=0.7,
            timeout=600,
        )
        rapid_agent = RapidAIAgent(RAPIDAI_API_KEY)
        logger.info("Components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise


server = Server("deep-research-agent")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return [
        Resource(
            uri="research://capabilities",
            name="Research Capabilities",
            description="Available research tools and data sources",
            mimeType="text/plain",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    if uri == "research://capabilities":
        return """Deep Research Agent Capabilities:

1. Social Media Research (RapidAI)
   - Twitter/X posts and trends
   - Instagram content analysis   
   - Reddit discussions and threads

2. Web Content Scraping
   - Google search results
   - Google news
   - Wikipedia articles
   - Reddit discussions
   - Medium articles
   - News sites (BBC, CNN)
   - Other web sources

3. AI-Powered Analysis
   - Categorized content summaries
   - Source-specific analysis
   - Enhanced generation with context

4. Output Format
   - Categorized summaries by source
   - Professional formatting
   - Comprehensive research report
"""
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="deep_research",
            description="Perform comprehensive AI-powered research with categorized summaries using main.py logic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The research question or topic to investigate"},
                    "start_date": {"type": "string", "description": "Optional start date in YYYY-MM-DD format"},
                    "end_date": {"type": "string", "description": "Optional end date in YYYY-MM-DD format"},
                    "max_sources": {"type": "integer", "description": "Maximum number of sources to scrape (default: 5)", "default": 5},
                },
                "required": ["query"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if name == "deep_research":
        return await perform_deep_research(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")

async def perform_deep_research(args: dict) -> list[TextContent]:
    query = args.get("query", "").strip()
    start_date = args.get("start_date", "").strip()
    end_date = args.get("end_date", "").strip()
    max_sources = args.get("max_sources", 5)

    if not query:
        return [TextContent(type="text", text="Error: Query cannot be empty")]

    try:
        global model, rapid_agent
        if model is None or rapid_agent is None:
            initialize_components()

        date_filter = {}
        if start_date:
            date_filter["start"] = start_date + "T00:00:00Z"
        if end_date:
            date_filter["end"] = end_date + "T23:59:59Z"

        logger.info(f"Starting research for query: {query}")
        initial_output = model.generate_text(query)

        urls, aggregated_content = [], ""
        try:
            rapidai_data = rapid_agent.fetch_data(query, max_results=max_sources)
            urls = rapidai_data.get("urls", [])
            aggregated_content = rapidai_data.get("content", "")
            logger.info(f"Retrieved {len(urls)} URLs from RapidAI")
        except Exception as e:
            logger.warning(f"RapidAI fetch failed: {e}")

        if not urls:
            logger.info("Generating URLs using url_generator...")
            urls = generate_urls(query)

        logger.info("Scraping URLs...")
        scraped_texts = [scrape_multiple_urls([url], max_urls=1) for url in urls[:max_sources]]

        logger.info("Categorizing scraped data...")
        categorized_data = categorize_scraped_data(urls, scraped_texts, aggregated_content)

        logger.info("Generating category summaries with fact check prompt...")
        final_sections = []
        for source, texts in categorized_data.items():
            combined_text = "\n\n".join(texts)
            summary = model.enhanced_generation(
                f"Summarize ONLY facts present in the following text from {source} for the query: {query}. "
                f"Do not invent or hallucinate. Return only structured headlines or facts that exactly appear in the input text. "
                f"If there is not enough relevant information, say \"Not enough explicit information found.\"",
                initial_output,
                combined_text,
                max_total_tokens=400,
                chunk_size=200,
                timeout=600,
            )
            final_sections.append(f"### {source} Summary\n{summary}")

        final_output = "\n\n".join(final_sections)
        return [TextContent(type="text", text=final_output)]

    except Exception as e:
        logger.error(f"Research failed: {e}")
        return [TextContent(type="text", text=f"Research failed: {str(e)}")]

async def main():
    try:
        initialize_components()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="deep-research-agent",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(),
                ),
            )
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
