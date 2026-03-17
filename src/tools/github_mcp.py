"""
GitHub MCP Tool — connects agents to GitHub via the Model Context Protocol.

This uses the official GitHub MCP Server to give agents the ability to:
  - Read files from any public repo
  - Search code across GitHub
  - List repository structure
  - Read commit history

The MCP server is run as a subprocess (stdio transport). No custom GitHub
API code needed — the server handles everything.

Setup:
  1. Install: npm install -g @modelcontextprotocol/server-github
  2. Set GITHUB_TOKEN in your .env file
  3. Agents automatically get GitHub tools when initialized
"""

from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools


async def get_github_tools(github_token: str) -> list:
    """
    Connect to the GitHub MCP server and return the tools it provides.

    The GitHub MCP server exposes tools like:
      - get_file_contents: Read any file from a GitHub repo
      - search_repositories: Search repos by keyword
      - search_code: Search code across GitHub
      - list_commits: View commit history
      - get_issue / list_issues: Read issues
      - create_issue: Create new issues

    Args:
        github_token: GitHub personal access token (PAT)

    Returns:
        List of tools that can be passed to an AutoGen AssistantAgent
    """
    server_params = StdioServerParams(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_TOKEN": github_token},
    )

    tools = await mcp_server_tools(server_params)
    return tools
