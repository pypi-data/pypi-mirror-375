from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Initialize MCP server
mcp = FastMCP("github")

# GitHub API base URL and headers
BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "mcp-github-server"
}


@mcp.tool()
async def get_user_info(username: str):
    """
    Fetches information about a GitHub user.

    Args:
        username: The username of the GitHub user.

    Returns:
        A dictionary containing user details.
    """
    url = f"{BASE_URL}/users/{username}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e)}
        except httpx.TimeoutException:
            return {"error": "Request timed out"}


@mcp.tool()
async def get_repo_info(owner: str, repo: str):
    """
    Fetches information about a GitHub repository.

    Args:
        owner: The username of the repository owner.
        repo: The name of the repository.

    Returns:
        A dictionary containing repository details.
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e)}
        except httpx.TimeoutException:
            return {"error": "Request timed out"}


@mcp.tool()
async def get_authenticated_user():
    """
    Fetches information about the authenticated GitHub user.

    Returns:
        A dictionary containing the authenticated user's details.
    """
    url = f"{BASE_URL}/user"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e)}
        except httpx.TimeoutException:
            return {"error": "Request timed out"}


def main():
    print("Running MCP server for GitHub!")


if __name__ == "__main__":
    mcp.run(transport="stdio")




