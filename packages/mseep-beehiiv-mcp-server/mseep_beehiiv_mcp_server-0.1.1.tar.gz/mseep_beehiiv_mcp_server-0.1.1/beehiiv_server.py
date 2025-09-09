# beehiiv_server.py

from typing import Any, Optional
import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("beehiiv")

BEEHIIV_API_KEY = os.getenv("BEEHIIV_API_KEY")
BASE_URL = "https://api.beehiiv.com/v2"
publication_id = os.getenv("BEEHIIV_PUBLICATION_ID")

async def beehiiv_request(
    method: str,
    path: str,
    params: Optional[dict[str, Any]] = None,
    json_body: Optional[dict[str, Any]] = None
) -> Optional[dict[str, Any]]:
    """
    Helper to call the beehiiv API v2.

    Args:
        method: HTTP method (GET, POST, etc.)
        path:   API path (e.g. '/publications')
        params: Query parameters
        json_body: Request JSON body
    """
    headers = {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{BASE_URL}{path}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method, url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}

@mcp.tool()
async def list_publications() -> str:
    """
    List all publications accessible with this API key.
    """
    data = await beehiiv_request("GET", "/publications")
    if not data or "data" not in data:
        return "Failed to fetch publications."
    pubs = data["data"]
    return "\n".join(f"{p['id']}: {p['name']}" for p in pubs)

@mcp.tool()
async def list_posts(publication_id: str) -> str:
    """
    List all posts for a given publication.

    Args:
        publication_id: e.g. 'pub_00000000-0000-0000-0000-000000000000'
    """
    params = {
        "order_by": "publish_date",
        "direction": "desc",
        "limit": 5,
        "status": "confirmed"
    }
    path = f"/publications/{publication_id}/posts"
    data = await beehiiv_request("GET", path, params=params)
    if not data or "data" not in data:
        return f"API error: {data.get('error', 'Unknown error')}"
    return "\n".join(f"{p['id']}: {p['title']}" for p in data["data"])

@mcp.tool()
async def get_post(publication_id: str, post_id: str) -> str:
    """
    Retrieve a single post by ID.

    Args:
        publication_id: ID of the publication
        post_id:        ID of the post
    """
    path = f"/publications/{publication_id}/posts/{post_id}"
    data = await beehiiv_request("GET", path)
    if not data or "data" not in data:
        return "Failed to fetch the post."
    post = data["data"]
    return (
        f"Title: {post.get('title')}\n"
        f"Subtitle: {post.get('subtitle')}\n"
        f"URL: {post.get('web_url')}\n"
        f"Status: {post.get('status')}\n"
        f"Authors: {post.get('authors')}"
    )

@mcp.tool()
async def get_post_content(publication_id: str, post_id: str) -> dict:
    """
    Retrieve a post's content as JSON to use as a template.

    Args:
        publication_id: ID of the publication
        post_id: ID of the post
    
    Returns:
        dict: JSON object containing post title, subtitle, and HTML content template
    """
    path = f"/publications/{publication_id}/posts/{post_id}"
    params = {
        "expand[]": "free_web_content"
    }
    
    data = await beehiiv_request("GET", path, params=params)
    
    if not data or "data" not in data:
        return {"error": "Failed to fetch the post."}
    
    post = data["data"]
    content = post.get("content", {})
    free_content = content.get("free", {})
    
    return {
        "title": post.get("title"),
        "subtitle": post.get("subtitle"),
        "content_structure": post.get("content_structure"),
        "html_template": free_content.get("web")
    }

@mcp.tool()
# have not tested this as I am not an enterprise customer, but leaving here for reference
async def create_new_post(publication_id: str, title: str, subtitle: str, html_content: str) -> str:
    """
    Create a new post using provided HTML content.

    Args:
        publication_id: ID of the publication
        title: Title of the new post
        subtitle: Subtitle of the new post
        html_content: HTML content for the post
    """
    path = f"/publications/{publication_id}/posts"
    
    post_data = {
        "title": title,
        "subtitle": subtitle,
        "content": {
            "free": {
                "web": html_content,
                "email": html_content,  # You might want to format this differently for email
                "rss": html_content    # And for RSS
            }
        }
    }
    
    response = await beehiiv_request("POST", path, json_body=post_data)
    
    if not response or "data" not in response:
        return f"Failed to create post: {response.get('error', 'Unknown error')}"
    
    new_post = response["data"]
    return {
        "status": "success",
        "post_id": new_post.get("id"),
        "web_url": new_post.get("web_url")
    }

if __name__ == "__main__":
    # Launch the MCP server
    mcp.run()



