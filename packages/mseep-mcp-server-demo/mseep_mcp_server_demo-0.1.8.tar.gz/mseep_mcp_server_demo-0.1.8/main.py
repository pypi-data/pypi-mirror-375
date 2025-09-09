# server.py
from mcp.server.fastmcp import FastMCP # type: ignore
import os

# Create an MCP server
mcp = FastMCP("AI Sticky Notes")

NOTES_FILE =os.path.join(os.path.dirname(__file__), "notes.txt")

def ensure_file():
    "Make sure that a file exists. If not, create it"
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

@mcp.tool()
def add_note(message: str) -> str:
    # the docstring is very important so the the mcp client (Claude desktop for instance)
    # can understand what this mcp tool does exactely 
    """
    Append a new note to the sticky note file

    Args:
        message (str): The note content to be added
    
    Returns:
        str: Confirmation message indicating the note was saved.
    """
    ensure_file()
    with open(NOTES_FILE, "a") as f: # opening it in append mode, not overriding but writing to the end.
        f.write(message + "\n")
    return "Note saved !"

@mcp.tool()
def read_notes() -> str:
    """
    Read and return all notes from the AI sticky note file.

    Returns:
        str: All notes as a single string separated by line breaks.
        If no notes exist, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    return content or "No notes yet."

@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """
    Read and return the latest note from the AI sticky note file.

    Returns:
        str: The last note saved.
        If no notes exist, a default message is returned.
    """
    ensure_file
    with open(NOTES_FILE, "r") as f:
        lines = f.readlines()
    return lines[-1].strip() if lines else "No notes yet."

@mcp.prompt()
def note_summary_prompt() -> str:
    """
    Generate a reusable prompt to summarize the AI sticky notes.

    Returns:
        str: A prompt string to summarize the AI sticky notes.
        If no notes exist, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    if not content:
        return "There are no notes yet."
    return f"Summarize the current notes: {content}"