import os
import json
import httpx
import inspect
from fastmcp import FastMCP
import logging
from typing import Dict, Any, Optional
from functools import wraps

# Create MCP Server
MCP_SERVER_NAME = "higress-ai-search-mcp-server"
mcp = FastMCP(MCP_SERVER_NAME)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Get Higress configuration from environment variables
HIGRESS_URL = os.getenv("HIGRESS_URL", "http://localhost:8080/v1/chat/completions")

# Get MODEL from environment variables (required)
MODEL = os.getenv("MODEL")
if not MODEL:
    raise ValueError("MODEL environment variable is required. Please set it to the LLM model you want to use.")

# Get knowledge base information from environment variables
INTERNAL_KNOWLEDGE_BASES = os.getenv("INTERNAL_KNOWLEDGE_BASES", "")
INTERNAL_KB_DESCRIPTION = f"👨‍💻 **Internal Knowledge Search**: {INTERNAL_KNOWLEDGE_BASES}" if INTERNAL_KNOWLEDGE_BASES else ""

def dynamic_docstring(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    base_doc = """
    Enhance AI model responses with real-time search results from search engines.
    
    This tool sends a query to Higress, which integrates with various search engines to provide up-to-date information:
    
    🌐 **Internet Search**: Google, Bing, Quark - for general web information
    📖 **Academic Search**: Arxiv - for scientific papers and research
    {internal_knowledge}
    
    Args:
        query: The user's question or search query
        
    Returns:
        The enhanced AI response with search results incorporated
    """.format(internal_knowledge=INTERNAL_KB_DESCRIPTION)
    
    # Update the function's docstring
    wrapper.__doc__ = base_doc
    return wrapper

@mcp.tool()
@dynamic_docstring
async def ai_search(query: str) -> Dict[str, Any]:
    """Dynamic docstring will be set by the decorator"""
    logger.info(f"Sending query to Higress: {query}")
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                HIGRESS_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0  # 30 seconds timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Higress: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "code": response.status_code,
                    "message": f"Higress returned an error: {response.text}"
                }
                
            result = response.json()
            logger.info(f"Received response from Higress")
            return result
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to connect to Higress: {str(e)}"
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to parse Higress response: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }

def main():
    """Entry point for the MCP server when run as a module."""
    logger.info(f"Starting {MCP_SERVER_NAME} with Higress at {HIGRESS_URL}")
    mcp.run()

if __name__ == "__main__":
    main()
