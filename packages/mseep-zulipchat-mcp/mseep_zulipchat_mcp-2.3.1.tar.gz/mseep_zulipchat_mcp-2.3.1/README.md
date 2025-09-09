# ZulipChat MCP Server

<div align="center">

**Connect AI assistants to Zulip Chat**

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)

[Quick Start](#quick-start) • [Installation](#installation) • [Tools](#available-tools) • [Examples](#examples)

</div>

## What is this?

ZulipChat MCP lets AI assistants like Claude, ChatGPT, and Cursor interact with your Zulip workspace. Send messages, search conversations, create summaries - all through natural language.

### Real Examples

```text
You: "Send a message to #general saying the deployment is complete"
AI: ✓ Message sent to #general

You: "What did people discuss in #engineering today?"
AI: Here's a summary of today's engineering discussions...

You: "Generate a daily summary of all active streams"
AI: Creating your daily digest...
```

## New in v2.3.0: Enhanced Production MCP Server

**🎉 22 MCP Tools with 100% Success Rate** - Comprehensive agent communication system:
- ✅ **Enhanced Tool Descriptions** - Agent-optimized descriptions with detailed examples and usage guidance
- ✅ **Advanced Search Capabilities** - Unicode emoji support, advanced syntax (`sender:`, `stream:`, `topic:` operators)
- ✅ **Robust Input Validation** - Comprehensive parameter validation with specific error messages
- ✅ **International Support** - Full Unicode support for stream names, emoji search, and international characters
- ✅ **Enhanced Error Handling** - Detailed validation feedback and recovery suggestions

**🚀 Advanced Agent Features**:
- 🤖 **Bot Identity** - Dual-credential system with sophisticated agent identity management
- 🔍 **Smart Search** - Advanced query parsing with `sender:alice@company.com stream:general Python` syntax
- 🌐 **Unicode Support** - Stream names with Chinese, Arabic, emoji characters (开发-🚀)
- 📊 **Task Management** - Complete lifecycle with progress validation (0-100%) and metadata tracking
- 💬 **Rich Communication** - Enhanced responses with metadata, timestamps, and operation context
- 🎯 **Agent-Optimized** - Detailed docstrings, examples, and validation rules for AI agents

**🛠️ Comprehensive MCP Tools** (22 total):
- **Messaging**: `send_message`, `edit_message`, `add_reaction`, `get_messages` (enhanced responses)
- **Streams**: `get_streams`, `create_stream`, `rename_stream`, `archive_stream` (Unicode support)
- **Agents**: `register_agent`, `agent_message`, `start_task`, `update_task_progress`, `complete_task`, `list_instances` 
- **Search**: `search_messages`, `get_daily_summary` (advanced syntax, emoji support)
- **AFK Management**: `enable_afk_mode`, `disable_afk_mode`, `get_afk_status`
- **User Interaction**: `request_user_input`, `wait_for_response`, `send_agent_status`

**⚡ Features**: Stream management, messaging, search, agent tracking, user interaction, metrics, and comprehensive database integration

## Quick Start

```bash
uvx --from git+https://github.com/akougkas/zulipchat-mcp.git zulipchat-mcp --zulip-email YOUR_EMAIL --zulip-api-key YOUR_API_KEY --zulip-site YOUR_SITE
```

> 🚀 **Development Release**: Currently installing directly from GitHub. PyPI package coming soon for simplified `uvx zulipchat-mcp` installation!

<details>
<summary><strong>💡 Tip: Shorten the command</strong></summary>

Create an alias to make the command shorter:
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
alias zulipchat-mcp-dev="uvx --from git+https://github.com/akougkas/zulipchat-mcp.git zulipchat-mcp"

# Then use:
zulipchat-mcp-dev --zulip-email YOUR_EMAIL --zulip-api-key YOUR_API_KEY --zulip-site YOUR_SITE
```

</details>

## Installation

<details>
<summary><strong>Install in Claude Desktop</strong></summary>

### Local Server Connection

Open Claude Desktop developer settings and edit your `claude_desktop_config.json` file to add the following configuration:

```json
{
  "mcpServers": {
    "zulipchat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/akougkas/zulipchat-mcp.git",
        "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>Install in Claude Code</strong></summary>

```bash
claude mcp add zulipchat -- uvx --from git+https://github.com/akougkas/zulipchat-mcp.git zulipchat-mcp --zulip-email YOUR_EMAIL --zulip-api-key YOUR_API_KEY --zulip-site YOUR_SITE
```

</details>

<details>
<summary><strong>Install in VS Code</strong></summary>

```json
{
  "mcp.servers": {
    "zulipchat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/akougkas/zulipchat-mcp.git",
        "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ],
      "type": "stdio"
    }
  }
}
```

</details>

<details>
<summary><strong>Install in Cursor</strong></summary>

```json
{
  "mcpServers": {
    "zulipchat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/akougkas/zulipchat-mcp.git",
        "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>Install in Gemini CLI</strong></summary>

```json
{
  "mcpServers": {
    "zulipchat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/akougkas/zulipchat-mcp.git",
        "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>Install in Opencode</strong></summary>

```json
{
  "mcp": {
    "zulipchat": {
      "type": "local",
      "command": [
        "uvx", "--from", "git+https://github.com/akougkas/zulipchat-mcp.git", "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ],
      "enabled": true
    }
  }
}
```

</details>

<details>
<summary><strong>Install in Crush CLI</strong></summary>

```json
{
  "mcpServers": {
    "zulipchat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/akougkas/zulipchat-mcp.git",
        "zulipchat-mcp",
        "--zulip-email", "YOUR_EMAIL",
        "--zulip-api-key", "YOUR_API_KEY",
        "--zulip-site", "YOUR_SITE"
      ]
    }
  }
}
```

</details>


## Available Tools

Your AI assistant can use these Zulip tools:

### Core Messaging Tools
| Tool | What it does | Example |
|------|--------------|---------|
| `send_message` | Send messages to streams or users | "Post update to #releases" |
| `get_messages` | Retrieve recent messages | "Show me the last 10 messages in #general" |
| `search_messages` | Search across all messages | "Find messages about deployment" |
| `get_streams` | List available streams | "What streams can I access?" |
| `get_users` | List organization users | "Who's in the workspace?" |
| `add_reaction` | Add emoji reactions | "React with 👍 to the last message" |
| `edit_message` | Edit existing messages | "Fix the typo in my last message" |
| `get_daily_summary` | Generate activity reports | "Create a summary of today's activity" |

### Agent Communication Tools (v1.4.0)
| Tool | What it does | Example |
|------|--------------|---------|
| `register_agent` | Register AI agent with auto-detection | "Register Claude Code for this project" |
| `agent_message` | Send project-aware notifications | "Notify completion of task" |
| `request_user_input` | Request input with context | "Ask which branch to deploy" |
| `send_agent_status` | Send status updates | "Update progress to 75%" |
| `start_task` | Start task with tracking | "Begin implementing auth feature" |
| `update_task_progress` | Update task progress | "Mark subtask as complete" |
| `complete_task` | Complete task with summary | "Finish task with test results" |
| `list_instances` | List all active instances | "Show all Claude Code instances" |

### Stream Management Tools
| Tool | What it does | Example |
|------|--------------|---------|
| `create_stream` | Create new streams | "Create stream for project-x" |
| `rename_stream` | Rename existing streams | "Rename stream to archived-project" |
| `archive_stream` | Archive streams | "Archive old project stream" |

## Resources

Access Zulip data directly:

- `zulip://stream/{name}` - Stream message history
- `zulip://streams` - All available streams
- `zulip://users` - Organization users

## Smart Prompts

Built-in prompts for common tasks:

- `daily_summary` - Comprehensive daily report
- `morning_briefing` - Overnight activity summary  
- `catch_up` - Quick summary of recent messages

## Examples

### Daily Standup Automation
```text
You: "Post our daily standup reminder to #team"
AI: ✓ Posted standup reminder with yesterday's summary
```

### Smart Search (Enhanced v2.3.0)
```text
You: "Find all messages from Alice about the API redesign"
AI: Found 12 messages from Alice discussing API redesign...

You: "Search for messages from alice@company.com in #development about Python"
AI: Using advanced search: sender:alice@company.com stream:development Python
    Found 8 messages matching your criteria...

You: "Find emoji reactions with 🚀 in project updates"
AI: Searching Unicode emoji: 🚀
    Found 15 messages with rocket emoji reactions...
```

### Activity Reports
```text
You: "Generate a weekly summary for #product"
AI: Here's your weekly product channel summary...
```

### International Team Support (New v2.3.0)
```text
You: "Create a stream called 'Development-开发-🚀' for our international team"
AI: ✓ Stream created with Unicode name: Development-开发-🚀

You: "Search for messages with Chinese characters about the project"
AI: Searching with Unicode support...
    Found 23 messages with Chinese characters...
```

### Message Management
```text
You: "Edit my last message to fix the meeting time to 3pm"
AI: ✓ Message updated with enhanced validation and metadata
```

## Configuration

Pass credentials as CLI arguments (recommended) or use environment variables for development:

```bash
# CLI arguments (for MCP clients)
--zulip-email YOUR_EMAIL --zulip-api-key YOUR_API_KEY --zulip-site YOUR_SITE

# Environment variables (for development)
export ZULIP_EMAIL="your-email@domain.com"
export ZULIP_API_KEY="your-api-key" 
export ZULIP_SITE="https://your-org.zulipchat.com"
```

## Development

### Local Setup
```bash
git clone https://github.com/akougkas/zulipchat-mcp.git
cd zulipchat-mcp
uv sync
uv run zulipchat-mcp
```

### Testing Connection
```bash
uvx --from git+https://github.com/akougkas/zulipchat-mcp.git zulipchat-mcp --help
```

## Troubleshooting

**"No Zulip email found"**
- Provide CLI arguments: `--zulip-email`, `--zulip-api-key`, `--zulip-site`
- Or set environment variables: `ZULIP_EMAIL`, `ZULIP_API_KEY`, `ZULIP_SITE`

**"Connection failed"**
- Verify your API key is correct and active
- Check your Zulip site URL includes `https://`
- Ensure your bot has permissions for the target streams

**MCP Connection Issues**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Reinstall: `uvx --from git+https://github.com/akougkas/zulipchat-mcp.git zulipchat-mcp`

## Use Cases

- **DevOps**: Automate deployment notifications and incident updates
- **Support**: Route customer questions and create ticket summaries
- **Product**: Generate sprint reports and feature request digests
- **Team Leads**: Daily standups and team activity summaries
- **HR**: Onboarding workflows and announcement automation

## Architecture

ZulipChat MCP is built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Pydantic](https://pydantic.dev) - Data validation
- [UV](https://docs.astral.sh/uv/) - Fast Python package management
- Async operations for performance
- Smart caching for efficiency
- Comprehensive error handling

## Contributing

We welcome contributions! To get started:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [AGENTS.md](AGENTS.md) for development guidelines.

## License

MIT - See [LICENSE](LICENSE) for details.

## Links

- [Zulip API Documentation](https://zulip.com/api/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Report Issues](https://github.com/akougkas/zulipchat-mcp/issues)

---

<div align="center">
  <sub>Built with ❤️ for the Zulip community</sub>
</div>