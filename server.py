# server.py
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS

# Create an MCP server
mcp = FastMCP("DemoServer")

# Simple tool
@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to someone

    Args:
        name: The person's name to greet
    """
    return f"Hello, {name}! Nice to meet you."

# Web search tool
@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information

    Args:
        query: The search query to look up
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return f"No results found for '{query}'"
        
        # Format results nicely
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            link = result.get('link', 'No link')
            formatted_results.append(f"{i}. {title}\n   {snippet}\n   Link: {link}\n")
        
        return f"Search results for '{query}':\n\n" + "\n".join(formatted_results)
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"

# Run the server
if __name__ == "__main__":
    mcp.run()