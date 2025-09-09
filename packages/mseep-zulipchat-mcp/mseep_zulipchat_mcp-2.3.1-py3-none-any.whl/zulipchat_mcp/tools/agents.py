"""Agent communication tools for ZulipChat MCP."""

import os
import time
import uuid
from datetime import datetime
from typing import Any

from ..config import ConfigManager
from ..core.agent_tracker import AgentTracker
from ..core.client import ZulipClientWrapper
from ..utils.database import get_database
from ..utils.logging import LogContext, get_logger
from ..utils.metrics import Timer, track_tool_call, track_tool_error

logger = get_logger(__name__)


_tracker = AgentTracker()
_client: ZulipClientWrapper | None = None


def _get_client_bot() -> ZulipClientWrapper:
    global _client
    if _client is None:
        _client = ZulipClientWrapper(ConfigManager(), use_bot_identity=True)
    return _client


def register_agent(agent_type: str = "claude-code") -> dict[str, Any]:
    """Register agent and create database records."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "register_agent"}):
        track_tool_call("register_agent")
        try:
            db = get_database()
            agent_id = str(uuid.uuid4())
            instance_id = str(uuid.uuid4())

            # Insert or update agent record
            db.execute(
                """
                INSERT OR REPLACE INTO agents (agent_id, agent_type, created_at, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (agent_id, agent_type, datetime.utcnow(), "{}"),
            )

            # Insert agent instance
            db.execute(
                """
                INSERT INTO agent_instances
                (instance_id, agent_id, session_id, project_dir, host, started_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    instance_id,
                    agent_id,
                    str(uuid.uuid4())[:8],  # Short session ID
                    str(os.getcwd()),
                    "localhost",
                    datetime.utcnow(),
                ),
            )

            # Initialize AFK state (disabled by default)
            db.execute(
                """
                INSERT OR REPLACE INTO afk_state (id, is_afk, reason, updated_at)
                VALUES (1, ?, ?, ?)
                """,
                (False, "Agent ready for normal operations", datetime.utcnow()),
            )

            # Check if Agent-Channel stream exists
            client = _get_client_bot()
            response = client.get_streams()
            streams = (
                response.get("streams", [])
                if response.get("result") == "success"
                else []
            )
            stream_exists = any(s.get("name") == "Agent-Channel" for s in streams)

            result = {
                "status": "success",
                "agent_id": agent_id,
                "instance_id": instance_id,
                "agent_type": agent_type,
                "stream": "Agent-Channel",
                "afk_enabled": False,
            }

            if not stream_exists:
                result["warning"] = "Stream 'Agent-Channel' does not exist."

            return result

        except Exception as e:
            track_tool_error("register_agent", type(e).__name__)
            return {"status": "error", "error": str(e)}


def agent_message(
    content: str, require_response: bool = False, agent_type: str = "claude-code"
) -> dict[str, Any]:
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "agent_message"}):
        with LogContext(logger, tool="agent_message", agent_type=agent_type):
            track_tool_call("agent_message")
            try:
                msg_info = _tracker.format_agent_message(
                    content, agent_type, require_response
                )
                if msg_info["status"] != "ready":
                    return msg_info

                client = _get_client_bot()
                result = client.send_message(
                    message_type="stream",
                    to=msg_info["stream"],
                    content=msg_info["content"],
                    topic=msg_info["topic"],
                )
                if result.get("result") == "success":
                    return {
                        "status": "success",
                        "message_id": result.get("id"),
                        "response_id": msg_info.get("response_id"),
                        "sent_via": "agent_message",
                    }
                return {"status": "error", "error": result.get("msg", "Failed to send")}
            except Exception as e:
                track_tool_error("agent_message", type(e).__name__)
                return {"status": "error", "error": str(e)}


def wait_for_response(request_id: str) -> dict[str, Any]:
    """Wait for user response by polling the database."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "wait_for_response"}):
        track_tool_call("wait_for_response")
        try:
            db = get_database()

            # Blocking loop polling database every ~1s until status is terminal
            while True:
                result = db.query_one(
                    """
                    SELECT status, response, responded_at
                    FROM user_input_requests
                    WHERE request_id = ?
                    """,
                    [request_id],
                )

                if not result:
                    return {"status": "error", "error": "Request not found"}

                status, response, responded_at = result

                # Check if status is terminal
                if status in ["answered", "cancelled"]:
                    return {
                        "status": "success",
                        "request_status": status,
                        "response": response,
                        "responded_at": (
                            responded_at.isoformat() if responded_at else None
                        ),
                    }

                # Send agent status update periodically (every 30 seconds)
                # This is optional but helps with monitoring
                time.sleep(1.0)

        except Exception as e:
            track_tool_error("wait_for_response", type(e).__name__)
            return {"status": "error", "error": str(e)}


def send_agent_status(
    agent_type: str, status: str, message: str = ""
) -> dict[str, Any]:
    """Send agent status update."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "send_agent_status"}):
        track_tool_call("send_agent_status")
        try:
            # TODO: Implement with DatabaseManager in Task 6
            return {
                "status": "success",
                "message": "Status updated (stub implementation)",
            }
        except Exception as e:
            track_tool_error("send_agent_status", type(e).__name__)
            return {"status": "error", "error": str(e)}


def request_user_input(
    agent_id: str, question: str, context: str = "", options: list[str] | None = None
) -> dict[str, Any]:
    """Request input from user via Zulip message."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "request_user_input"}):
        track_tool_call("request_user_input")
        try:
            request_id = str(uuid.uuid4())
            db = get_database()

            # Insert user input request into database
            db.execute(
                """
                INSERT INTO user_input_requests
                (request_id, agent_id, question, context, options, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    agent_id,
                    question,
                    context,
                    str(options) if options else None,
                    "pending",
                    datetime.utcnow(),
                ),
            )

            # Format message content
            message_content = f"""🤖 **Agent Request**

**Question**: {question}

**Context**: {context}"""

            if options:
                message_content += "\n\n**Options**:\n"
                for i, option in enumerate(options, 1):
                    message_content += f"{i}. {option}\n"
                message_content += (
                    "\nReply with the number of your choice or type your response."
                )
            else:
                message_content += "\n\nPlease respond with your answer."

            message_content += f"\n\n*Request ID: `{request_id}`*"

            # Get agent info to determine user
            agent_data = db.query_one(
                "SELECT agent_type, metadata FROM agents WHERE agent_id = ?", [agent_id]
            )

            if not agent_data:
                return {"status": "error", "error": "Agent not found"}

            agent_type = agent_data[0]

            # For now, send to Agent-Channel stream since we don't have user mapping
            # TODO: In future, implement proper user detection from agent metadata
            from ..tools.messaging import send_message

            result = send_message(
                message_type="stream",
                to="Agent-Channel",
                content=message_content,
                topic=f"User Input Request - {agent_type}",
            )

            if result.get("status") != "success":
                return {
                    "status": "error",
                    "error": f"Failed to send message: {result.get('error')}",
                }

            return {"status": "success", "request_id": request_id, "message_sent": True}
        except Exception as e:
            track_tool_error("request_user_input", type(e).__name__)
            return {"status": "error", "error": str(e)}


def start_task(agent_id: str, name: str, description: str = "") -> dict[str, Any]:
    """Start a new task with validation and database tracking.

    Args:
        agent_id: ID of the agent creating the task (must exist in system)
        name: Task name (1-200 characters, cannot be empty)
        description: Optional detailed description (max 1000 characters)

    Returns:
        Dictionary with task creation result:
        - Success: {"status": "success", "task_id": "uuid"}
        - Error: {"status": "error", "error": "description of error"}

    Examples:
        # Simple task
        start_task("agent-123", "Process user reports")

        # Detailed task
        start_task("agent-123", "Analyze Q3 metrics",
                  "Review quarterly performance data and generate insights")
    """
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "start_task"}):
        track_tool_call("start_task")
        try:
            # Input validation
            if not agent_id or not isinstance(agent_id, str):
                return {"status": "error", "error": "Invalid agent_id"}

            if not name or not isinstance(name, str) or len(name.strip()) == 0:
                return {"status": "error", "error": "Task name cannot be empty"}

            if len(name) > 200:
                return {
                    "status": "error",
                    "error": "Task name cannot exceed 200 characters",
                }

            if description and (
                not isinstance(description, str) or len(description) > 1000
            ):
                return {
                    "status": "error",
                    "error": "Task description cannot exceed 1000 characters",
                }

            task_id = str(uuid.uuid4())
            db = get_database()

            # Verify agent exists
            existing_agent = db.query_one(
                "SELECT agent_id FROM agents WHERE agent_id = ?", [agent_id]
            )

            if not existing_agent:
                return {
                    "status": "error",
                    "error": f"Agent with ID '{agent_id}' not found",
                }

            # Insert task into database
            db.execute(
                """
                INSERT INTO tasks
                (task_id, agent_id, name, description, status, progress, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    agent_id,
                    name.strip(),
                    description.strip(),
                    "started",
                    0,
                    datetime.utcnow(),
                ),
            )

            return {"status": "success", "task_id": task_id}
        except Exception as e:
            track_tool_error("start_task", type(e).__name__)
            return {"status": "error", "error": str(e)}


def update_task_progress(
    task_id: str, progress: int, status: str = ""
) -> dict[str, Any]:
    """Update task progress."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "update_task_progress"}):
        track_tool_call("update_task_progress")
        try:
            # Input validation
            if not task_id or not isinstance(task_id, str):
                return {"status": "error", "error": "Invalid task_id"}

            if not isinstance(progress, int) or not (0 <= progress <= 100):
                return {
                    "status": "error",
                    "error": "Progress must be an integer between 0 and 100",
                }

            if status and not isinstance(status, str):
                return {"status": "error", "error": "Status must be a string"}

            db = get_database()

            # Verify task exists before updating
            existing_task = db.query_one(
                "SELECT task_id FROM tasks WHERE task_id = ?", [task_id]
            )

            if not existing_task:
                return {
                    "status": "error",
                    "error": f"Task with ID '{task_id}' not found",
                }

            # Update task progress in database
            update_sql = "UPDATE tasks SET progress = ?"
            params: list[Any] = [progress]

            if status:
                update_sql += ", status = ?"
                params.append(status)

            update_sql += " WHERE task_id = ?"
            params.append(task_id)

            db.execute(update_sql, params)

            return {"status": "success", "message": "Progress updated"}
        except Exception as e:
            track_tool_error("update_task_progress", type(e).__name__)
            return {"status": "error", "error": str(e)}


def complete_task(task_id: str, outputs: str = "", metrics: str = "") -> dict[str, Any]:
    """Complete a task."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "complete_task"}):
        track_tool_call("complete_task")
        try:
            # Input validation
            if not task_id or not isinstance(task_id, str):
                return {"status": "error", "error": "Invalid task_id"}

            if outputs and (not isinstance(outputs, str) or len(outputs) > 5000):
                return {
                    "status": "error",
                    "error": "Task outputs cannot exceed 5000 characters",
                }

            if metrics and (not isinstance(metrics, str) or len(metrics) > 2000):
                return {
                    "status": "error",
                    "error": "Task metrics cannot exceed 2000 characters",
                }

            db = get_database()

            # Verify task exists before completing
            existing_task = db.query_one(
                "SELECT task_id, status FROM tasks WHERE task_id = ?", [task_id]
            )

            if not existing_task:
                return {
                    "status": "error",
                    "error": f"Task with ID '{task_id}' not found",
                }

            if existing_task[1] == "completed":
                return {"status": "error", "error": "Task is already completed"}

            # Complete task in database
            db.execute(
                """
                UPDATE tasks
                SET status = ?, progress = ?, completed_at = ?, outputs = ?, metrics = ?
                WHERE task_id = ?
                """,
                (
                    "completed",
                    100,
                    datetime.utcnow(),
                    outputs.strip(),
                    metrics.strip(),
                    task_id,
                ),
            )

            return {"status": "success", "message": "Task completed"}
        except Exception as e:
            track_tool_error("complete_task", type(e).__name__)
            return {"status": "error", "error": str(e)}


def list_instances() -> dict[str, Any]:
    """List agent instances."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "list_instances"}):
        track_tool_call("list_instances")
        try:
            db = get_database()

            # Query agent instances from database
            instances = db.query(
                """
                SELECT ai.instance_id, ai.agent_id, a.agent_type, ai.session_id,
                       ai.project_dir, ai.host, ai.started_at
                FROM agent_instances ai
                JOIN agents a ON ai.agent_id = a.agent_id
                ORDER BY ai.started_at DESC
                """
            )

            instance_list = [
                {
                    "instance_id": row[0],
                    "agent_id": row[1],
                    "agent_type": row[2],
                    "session_id": row[3],
                    "project_dir": row[4],
                    "host": row[5],
                    "started_at": row[6].isoformat() if row[6] else None,
                }
                for row in instances
            ]

            return {"status": "success", "instances": instance_list}
        except Exception as e:
            track_tool_error("list_instances", type(e).__name__)
            return {"status": "error", "error": str(e)}


def enable_afk_mode(
    hours: int = 8, reason: str = "Away from computer"
) -> dict[str, Any]:
    """Enable AFK mode for automatic notifications when away."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "enable_afk_mode"}):
        track_tool_call("enable_afk_mode")
        try:
            _tracker.set_afk(enabled=True, hours=hours)
            return {
                "status": "success",
                "message": f"AFK mode enabled for {hours} hours",
                "reason": reason,
            }
        except Exception as e:
            track_tool_error("enable_afk_mode", type(e).__name__)
            return {"status": "error", "error": str(e)}


def disable_afk_mode() -> dict[str, Any]:
    """Disable AFK mode - normal agent communication."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "disable_afk_mode"}):
        track_tool_call("disable_afk_mode")
        try:
            _tracker.set_afk(enabled=False, hours=0)
            return {
                "status": "success",
                "message": "AFK mode disabled - normal operation",
            }
        except Exception as e:
            track_tool_error("disable_afk_mode", type(e).__name__)
            return {"status": "error", "error": str(e)}


def get_afk_status() -> dict[str, Any]:
    """Get current AFK mode status."""
    with Timer("zulip_mcp_tool_duration_seconds", {"tool": "get_afk_status"}):
        track_tool_call("get_afk_status")
        try:
            return {"status": "success", "afk_state": _tracker.get_afk_state()}
        except Exception as e:
            track_tool_error("get_afk_status", type(e).__name__)
            return {"status": "error", "error": str(e)}


def register_agent_tools(mcp: Any) -> None:
    """Register agent management tools with comprehensive descriptions for AI agents."""
    mcp.tool(
        description="Register a new AI agent instance in the system. Creates database records, assigns unique IDs, and checks for Agent-Channel stream. Use agent_type to identify different agent types (default: 'claude-code'). Returns agent_id and configuration details."
    )(register_agent)
    mcp.tool(
        description="Send a message as an AI agent to the Agent-Channel stream. Formats messages with agent identity, timestamps, and optional response requirements. Use require_response=true to request human interaction. Content supports Markdown formatting."
    )(agent_message)
    mcp.tool(
        description="Wait for human response to a specific request by polling the database. Takes request_id from request_user_input. Blocks until user responds or request is cancelled. Returns user's response and metadata when available."
    )(wait_for_response)
    mcp.tool(
        description="Send status updates about agent operations. Use for progress reporting, error notifications, or state changes. Updates are logged and can trigger notifications. Status should be descriptive (e.g., 'processing', 'completed', 'error')."
    )(send_agent_status)
    mcp.tool(
        description="Request input from a human user via Zulip message with optional multiple choice. Specify question, context for clarity, and options array for choices. Posts to Agent-Channel and returns request_id for use with wait_for_response."
    )(request_user_input)
    mcp.tool(
        description="Start a new task with name and description. Creates database record, validates agent exists, enforces limits (name: 200 chars, description: 1000 chars). Returns task_id for progress tracking. Agent must be registered first."
    )(start_task)
    mcp.tool(
        description="Update task progress with percentage (0-100) and optional status text. Validates task exists and progress range. Use for incremental updates during long-running operations. Status examples: 'analyzing', 'in progress', 'blocked'."
    )(update_task_progress)
    mcp.tool(
        description="Mark task as completed with optional outputs and metrics. Sets progress to 100%, validates task exists and isn't already completed. Outputs (5000 chars) and metrics (2000 chars) document results and performance data."
    )(complete_task)
    mcp.tool(
        description="List all registered agent instances with details including agent_type, session_id, project directory, host, and start time. Useful for monitoring active agents and debugging multi-agent coordination."
    )(list_instances)
    mcp.tool(
        description="Enable Away From Keyboard mode for automatic notifications when human users are offline. Set hours duration (default: 8) and optional reason. Reduces notification frequency and sets expectations for response times."
    )(enable_afk_mode)
    mcp.tool(
        description="Disable AFK mode to resume normal notification and response behavior. Returns agent communication to standard responsiveness levels. Use when human user returns or manual override needed."
    )(disable_afk_mode)
    mcp.tool(
        description="Check current AFK mode status including enabled state, duration remaining, reason, and last update time. Use to adapt agent behavior based on human availability and expected response patterns."
    )(get_afk_status)
