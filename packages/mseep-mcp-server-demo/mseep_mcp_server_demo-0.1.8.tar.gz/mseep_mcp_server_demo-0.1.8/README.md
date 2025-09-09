# mcp-server-demo (AI sticky notes)
AI Sticky Notes: A Model Context Protocol (MCP) application that enables Claude Desktop to create, read, and manage persistent sticky notes.

# Overview
AI Sticky Notes leverages the Model Context Protocol to provide a seamless integration between Claude Desktop and a simple note-taking system. This implementation allows Claude to:

- Save notes to persistent storage
- Retrieve all saved notes
- Access the most recently added note
- Generate prompts to summarize existing notes

# Installation

# Prerequisites

- Python 3.7+
- MCP Python SDK
- Claude Desktop application

# Setup
1. Clone this repository:

    - `git clone https://github.com/aymaneELHICHAMI/mcp-server-demo.git`
    - `cd mcp-server-demo`

2. Install `uv`

    - Documentation: https://docs.astral.sh/uv/getting-started/installation/

3. Create a virtual environment

    - `uv venv venv`

4. Activate the virtual environment

    - `uv venv`

5. Install dependencies from `uv.lock`

    - `uv sync`

6. Run the MCP server
    - `uv run mcp install main.py`
    If the configuration is not reflected in Claude Desktop (Menu Bar -> Settings -> Developer), Try to force shutdown Claude Desktop from task Manager et reopen it. When working, you should see "AI Sticky Notes MCP Server" running.

# Core Components

```
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("AI Sticky Notes")
```

The server registers itself as "AI Sticky Notes" in the MCP ecosystem, making it discoverable by clients like Claude Desktop.

Notes are stored in a simple text file (notes.txt), with each note on a separate line. The file is automatically created if it doesn't exist.

The server exposes the following MCP capabilities:

| Type     | Name                  | Description                             |
|----------|-----------------------|-----------------------------------------|
| Tool     | `add_note`            | Append a new note to storage            |
| Tool     | `read_notes`          | Retrieve all existing notes             |
| Resource | `notes://latest`      | Access the most recent note             |
| Prompt   | `note_summary_prompt` | Generate a prompt for summarizing notes |


# Using with Claude Desktop
Once the server is running, Claude Desktop will automatically discover and connect to it. You can interact with your notes through natural language:

```
You: "Please save this as a note: Remember to schedule a team meeting for Friday"
Claude: [Uses add_note tool] "Note saved!"

You: "What notes do I have?"
Claude: [Uses read_notes tool] "Here are your notes: ..."

You: "What was my most recent note?"
Claude: [Accesses notes://latest resource] "Your most recent note is: ..."

You: "Can you summarize my notes?"
Claude: [Uses note_summary_prompt] "Here's a summary of your notes: ..."
```

# Resources

- Model Context Protocol Documentation: https://modelcontextprotocol.io/introduction

- FastMCP API Reference: https://github.com/jlowin/fastmcp

- Claude Desktop Documentation: https://docs.anthropic.com/en/docs/welcome