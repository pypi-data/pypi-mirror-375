"""Search and summary tools for ZulipChat MCP.

Optimized for latency with direct dict manipulation.
"""

import re
from datetime import datetime
from typing import Any

from ..config import ConfigManager
from ..core.client import ZulipClientWrapper
from ..core.security import sanitize_input
from ..utils.logging import LogContext, get_logger
from ..utils.metrics import Timer, track_tool_call, track_tool_error

logger = get_logger(__name__)

# Maximum content size (50KB) - reasonable for most LLMs
MAX_CONTENT_SIZE = 50000

_client: ZulipClientWrapper | None = None


def _get_client() -> ZulipClientWrapper:
    """Get or create client instance."""
    global _client
    if _client is None:
        _client = ZulipClientWrapper(ConfigManager(), use_bot_identity=False)
    return _client


def _truncate_content(content: str) -> str:
    """Truncate content if it exceeds maximum size."""
    if len(content) > MAX_CONTENT_SIZE:
        return content[:MAX_CONTENT_SIZE] + "\n... [Content truncated]"
    return content


def _parse_search_query(query: str) -> tuple[list[dict[str, str]], str]:
    """Parse advanced Zulip search syntax into narrow filters.

    Supports operators: sender:, from:, stream:, topic:, has:, is:, near:

    Args:
        query: The search query with possible operators

    Returns:
        Tuple of (narrow_filters, remaining_text_search)
    """
    narrow_filters = []
    remaining_query = query

    # Define supported operators and their Zulip narrow equivalents
    operators = {
        r"sender:([^\s]+)": "sender",
        r"from:([^\s]+)": "sender",  # Alias for sender
        r"stream:([^\s]+)": "stream",
        r"topic:([^\s]+)": "topic",
        r"has:([^\s]+)": "has",
        r"is:([^\s]+)": "is",
        r"near:([^\s]+)": "near",
    }

    # Extract operators and build narrow filters
    for pattern, operator in operators.items():
        matches = re.finditer(pattern, query, re.IGNORECASE)
        for match in matches:
            operand = match.group(1)
            # Remove quotes if present
            operand = operand.strip("'\"")

            narrow_filters.append({"operator": operator, "operand": operand})

            # Remove this match from the remaining query
            remaining_query = remaining_query.replace(match.group(0), " ").strip()

    # Clean up remaining query - remove extra spaces
    remaining_query = re.sub(r"\s+", " ", remaining_query).strip()

    return narrow_filters, remaining_query


def search_messages(query: str, limit: int = 50) -> dict[str, Any]:
    """Search Zulip messages with advanced syntax support and Unicode handling.

    Args:
        query: Search query with optional operators:
            - Plain text: "bug report"
            - Advanced: "sender:alice@company.com stream:general Python"
            - Operators: sender:, from:, stream:, topic:, has:, is:, near:
        limit: Maximum results to return (1-100, default: 50)

    Returns:
        Dictionary with search results and metadata:
        - Success: {"status": "success", "messages": [...], "count": int,
                   "search_params": {...}, "timestamp": "..."}
        - Error: {"status": "error", "error": "description of error"}

    Examples:
        # Simple text search
        search_messages("database migration")

        # Advanced filtered search
        search_messages("sender:alice@company.com stream:development Python bug", limit=25)
    """
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "search_messages"}):
        with LogContext(logger, tool="search_messages", query=query[:50]):
            track_tool_call("search_messages")
            try:
                # Input validation
                if not query:
                    return {"status": "error", "error": "Query cannot be empty"}
                if not (1 <= limit <= 100):
                    return {
                        "status": "error",
                        "error": "limit must be between 1 and 100",
                    }

                client = _get_client()
                safe_query = sanitize_input(query, preserve_unicode=True)

                # Parse advanced search syntax
                narrow_filters, text_query = _parse_search_query(safe_query)

                # Get raw response from Zulip with parsed filters
                response = client.search_messages_advanced(
                    narrow_filters, text_query, num_results=limit
                )

                # Quick validation
                if response.get("result") != "success":
                    return {
                        "status": "error",
                        "error": response.get("msg", "Search failed"),
                    }

                # Extract only essential fields - no model creation
                messages = [
                    {
                        "id": msg["id"],
                        "sender": msg["sender_full_name"],
                        "email": msg["sender_email"],
                        "timestamp": msg["timestamp"],
                        "content": _truncate_content(msg["content"]),
                        "type": msg["type"],
                        "stream": msg.get("display_recipient"),
                        "topic": msg.get("subject"),
                    }
                    for msg in response.get("messages", [])
                ]

                return {
                    "status": "success",
                    "messages": messages,
                    "count": len(messages),
                    "query": safe_query,
                    "search_params": {
                        "original_query": query,
                        "parsed_filters": narrow_filters,
                        "text_search": text_query,
                        "limit": limit,
                        "advanced_search": bool(narrow_filters),
                    },
                    "retrieved_via": "search_messages",
                    "timestamp": datetime.now().isoformat(),
                }

            except KeyError as e:
                track_tool_error("search_messages", "KeyError")
                logger.error(f"search_messages KeyError: {e}")
                return {"status": "error", "error": f"Missing expected field: {e}"}
            except Exception as e:
                track_tool_error("search_messages", type(e).__name__)
                logger.error(f"search_messages error: {type(e).__name__}: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Failed to search messages: {str(e)}",
                }


def get_daily_summary(
    streams: list[str] | None = None, hours_back: int = 24
) -> dict[str, Any]:
    """Get daily summary of messages."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "get_daily_summary"}):
        with LogContext(logger, tool="get_daily_summary"):
            track_tool_call("get_daily_summary")
            try:
                # Input validation
                if not (1 <= hours_back <= 168):
                    return {
                        "status": "error",
                        "error": "hours_back must be between 1 and 168",
                    }

                client = _get_client()
                data = client.get_daily_summary(streams, hours_back)

                # Check for errors from client
                if "error" in data:
                    return {"status": "error", "error": data["error"]}

                return {"status": "success", "data": data}

            except KeyError as e:
                track_tool_error("get_daily_summary", "KeyError")
                logger.error(f"get_daily_summary KeyError: {e}")
                return {"status": "error", "error": f"Missing expected field: {e}"}
            except Exception as e:
                track_tool_error("get_daily_summary", type(e).__name__)
                logger.error(f"get_daily_summary error: {type(e).__name__}: {str(e)}")
                return {"status": "error", "error": f"Failed to get summary: {str(e)}"}


def register_search_tools(mcp: Any) -> None:
    """Register search tools with comprehensive agent-friendly descriptions."""
    mcp.tool(
        description="Search Zulip messages with advanced syntax. Supports text queries, emoji/Unicode, and operators like 'sender:email', 'stream:name', 'topic:subject'. Use limit (1-100) to control results. Example: 'sender:alice@company.com stream:general Python' finds Python mentions from Alice in #general."
    )(search_messages)
    mcp.tool(
        description="Generate daily activity summary for specified streams over recent hours. Use streams=['stream1','stream2'] to filter, hours_back (1-168) for time range. Returns message counts, active users, popular topics, and key discussions. Default: all streams, 24 hours."
    )(get_daily_summary)
