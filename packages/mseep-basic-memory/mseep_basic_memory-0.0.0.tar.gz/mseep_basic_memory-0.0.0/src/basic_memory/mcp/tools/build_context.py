"""Build context tool for Basic Memory MCP server."""

from typing import Optional

from loguru import logger

from basic_memory.mcp.async_client import client
from basic_memory.mcp.server import mcp
from basic_memory.mcp.tools.utils import call_get
from basic_memory.mcp.project_session import get_active_project
from basic_memory.schemas.base import TimeFrame
from basic_memory.schemas.memory import (
    GraphContext,
    MemoryUrl,
    memory_url_path,
)

type StringOrInt = str | int


@mcp.tool(
    description="""Build context from a memory:// URI to continue conversations naturally.
    
    Use this to follow up on previous discussions or explore related topics.
    
    Memory URL Format:
    - Use paths like "folder/note" or "memory://folder/note" 
    - Pattern matching: "folder/*" matches all notes in folder
    - Valid characters: letters, numbers, hyphens, underscores, forward slashes
    - Avoid: double slashes (//), angle brackets (<>), quotes, pipes (|)
    - Examples: "specs/search", "projects/basic-memory", "notes/*"
    
    Timeframes support natural language like:
    - "2 days ago", "last week", "today", "3 months ago"
    - Or standard formats like "7d", "24h"
    """,
)
async def build_context(
    url: MemoryUrl,
    depth: Optional[StringOrInt] = 1,
    timeframe: Optional[TimeFrame] = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: Optional[str] = None,
) -> GraphContext:
    """Get context needed to continue a discussion.

    This tool enables natural continuation of discussions by loading relevant context
    from memory:// URIs. It uses pattern matching to find relevant content and builds
    a rich context graph of related information.

    Args:
        url: memory:// URI pointing to discussion content (e.g. memory://specs/search)
        depth: How many relation hops to traverse (1-3 recommended for performance)
        timeframe: How far back to look. Supports natural language like "2 days ago", "last week"
        page: Page number of results to return (default: 1)
        page_size: Number of results to return per page (default: 10)
        max_related: Maximum number of related results to return (default: 10)
        project: Optional project name to build context from. If not provided, uses current active project.

    Returns:
        GraphContext containing:
            - primary_results: Content matching the memory:// URI
            - related_results: Connected content via relations
            - metadata: Context building details

    Examples:
        # Continue a specific discussion
        build_context("memory://specs/search")

        # Get deeper context about a component
        build_context("memory://components/memory-service", depth=2)

        # Look at recent changes to a specification
        build_context("memory://specs/document-format", timeframe="today")

        # Research the history of a feature
        build_context("memory://features/knowledge-graph", timeframe="3 months ago")

        # Build context from specific project
        build_context("memory://specs/search", project="work-project")
    """
    logger.info(f"Building context from {url}")

    # Convert string depth to integer if needed
    if isinstance(depth, str):
        try:
            depth = int(depth)
        except ValueError:
            from mcp.server.fastmcp.exceptions import ToolError

            raise ToolError(f"Invalid depth parameter: '{depth}' is not a valid integer")

    # URL is already validated and normalized by MemoryUrl type annotation

    # Get the active project first to check project-specific sync status
    active_project = get_active_project(project)

    # Check migration status and wait briefly if needed
    from basic_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        # Return a proper GraphContext with status message
        from basic_memory.schemas.memory import MemoryMetadata
        from datetime import datetime

        return GraphContext(
            results=[],
            metadata=MemoryMetadata(
                depth=depth or 1,
                timeframe=timeframe,
                generated_at=datetime.now().astimezone(),
                primary_count=0,
                related_count=0,
                uri=migration_status,  # Include status in metadata
            ),
        )
    project_url = active_project.project_url

    response = await call_get(
        client,
        f"{project_url}/memory/{memory_url_path(url)}",
        params={
            "depth": depth,
            "timeframe": timeframe,
            "page": page,
            "page_size": page_size,
            "max_related": max_related,
        },
    )
    return GraphContext.model_validate(response.json())
