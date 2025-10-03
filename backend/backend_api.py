from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Add the MCP client (fix import path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mcp_client import DeepResearchMCPClient

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-api")

# Global MCP client
mcp_client = None

def get_mcp_client():
    """Get or create MCP client instance"""
    global mcp_client
    if mcp_client is None:
        mcp_client = DeepResearchMCPClient()
    return mcp_client

@app.route('/api/research', methods=['POST'])
def research_query():
    """Handle research requests via MCP server"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        max_sources = data.get('max_sources', 5)

        logger.info(f"Received research request: {user_query}")

        if not user_query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Use asyncio to call the MCP client
        async def perform_research():
            client = get_mcp_client()
            result = await client.research(
                query=user_query,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None,
                max_sources=max_sources
            )
            return result

        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(perform_research())
            logger.info(f"Research completed successfully")
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'final_summary': result,
            'query': user_query,
            'sources_requested': max_sources
        })

    except Exception as e:
        logger.error(f"Research error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get MCP server capabilities"""
    try:
        async def fetch_capabilities():
            client = get_mcp_client()
            return await client.get_capabilities()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            capabilities = loop.run_until_complete(fetch_capabilities())
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'capabilities': capabilities
        })

    except Exception as e:
        logger.error(f"Capabilities error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Deep Research Agent MCP API is running',
        'version': '1.0.0'
    })

# Cleanup on shutdown
@app.teardown_appcontext
def cleanup_mcp_client(error):
    """Cleanup MCP client connections"""
    global mcp_client
    if mcp_client:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(mcp_client.disconnect())
            loop.close()
        except:
            pass  # Ignore cleanup errors

if __name__ == '__main__':
    print("🚀 Starting Deep Research Agent MCP API...")
    print("🔌 MCP Server integration enabled")
    print("🌐 API running on http://localhost:5000")
    print("📊 Frontend should connect to http://localhost:3000")

    app.run(debug=True, host='0.0.0.0', port=5000)
