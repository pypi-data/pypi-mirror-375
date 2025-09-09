import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

DOVETAIL_URL="https://dovetail.com/api/v1"
DOVETAIL_API_TOKEN=""

# Create MCP server instance
mcp = FastMCP("mcp-hello-server")

@mcp.prompt()
def explain_thoughts(name: str) -> list[base.Message]:
    return [
        # Attempt at a system prompt
        # base.SystemPrompt("You're a user researcher who is analyzing feedback on Zotify, a spotify competitor"),
        base.UserMessage("You're a user researcher who is analyzing feedback on Zotify, a spotify competitor."),
        base.UserMessage("You have access to Dovetail."),
        base.UserMessage(f"Tell me about what {name} thinks, finding all notes where she expresses her opinion.")
    ]

@mcp.resource("info://app")
def get_app_info():
    with open("README.md", "r") as file:
        readme = file.read()
        return readme

@mcp.tool()
async def get_project_highlights(project_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/highlights?filter[project_id]={project_id}",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_project_insight(insight_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/insights/{insight_id}",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def list_project_insights(project_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/insights?filter[project_id]={project_id}",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_data_content(data_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/data/{data_id}/export/markdown",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_project_data(data_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/data/{data_id}",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def list_project_data(project_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/data?filter[project_id]={project_id}",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_dovetail_projects():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DOVETAIL_URL}/projects",
            headers={"Authorization": f"Bearer {DOVETAIL_API_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()


def main():
    """Main entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()