from typing import Any
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("catfacts")

# Constants
CAT_FACTS_API = "https://catfact.ninja/fact"
USER_AGENT = "catfacts-app/1.0"


async def get_cat_fact() -> dict[str, Any] | None:
    """Get a random cat fact from the API."""
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CAT_FACTS_API, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def single_cat_fact() -> str:
    """Get a single random cat fact."""
    data = await get_cat_fact()
    
    if not data or "fact" not in data:
        return "Hi! Sorry, I couldn't fetch a cat fact right now."
    
    return f"Hi! {data['fact']}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="sse")