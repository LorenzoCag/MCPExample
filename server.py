# server.py
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import praw

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

# Reddit scraping tool
@mcp.tool()
def reddit_scrape(subreddit: str) -> str:
    """Get top posts from a subreddit

    Args:
        subreddit: The name of the subreddit to scrape (without r/)
    """
    try:
        # Initialize Reddit client (using read-only mode)
        reddit = praw.Reddit(
            client_id="your_client_id",  # You'll need to get these from Reddit
            client_secret="your_client_secret",
            user_agent="MCPAgent/1.0"
        )
        
        # Get the subreddit
        subreddit_obj = reddit.subreddit(subreddit)
        
        # Get top posts
        posts = []
        for post in subreddit_obj.hot(limit=5):
            posts.append({
                'title': post.title,
                'score': post.score,
                'url': f"https://reddit.com{post.permalink}",
                'author': str(post.author),
                'comments': post.num_comments
            })
        
        if not posts:
            return f"No posts found in r/{subreddit}"
        
        # Format results
        formatted_posts = []
        for i, post in enumerate(posts, 1):
            formatted_posts.append(
                f"{i}. {post['title']}\n"
                f"   Score: {post['score']} | Comments: {post['comments']} | Author: {post['author']}\n"
                f"   URL: {post['url']}\n"
            )
        
        return f"Top posts from r/{subreddit}:\n\n" + "\n".join(formatted_posts)
    
    except Exception as e:
        return f"Error scraping Reddit: {str(e)}"

# Run the server
if __name__ == "__main__":
    mcp.run()