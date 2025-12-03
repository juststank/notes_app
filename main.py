from fastmcp import FastMCP
from dotenv import load_dotenv
import os
from pathlib import Path
import random
import logging

# Set up logging (important for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

mcp = FastMCP(name="Notes App")

NOTES_FILE = Path("notes.txt")

@mcp.tool()
def get_my_notes() -> str:
    """Get all notes for a user"""
    try:
        if not NOTES_FILE.exists():
            return "No notes found"
        
        notes = NOTES_FILE.read_text().strip().split('\n')
        if not notes or notes == ['']:
            return "No notes found"
        
        logger.info(f"Retrieved {len(notes)} notes")
        return "\n".join([f"{i+1}. {note}" for i, note in enumerate(notes) if note])
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        return f"Error retrieving notes: {str(e)}"


@mcp.tool()
def add_note(content: str) -> str:
    """Add a note for a user
    
    Args:
        content: The note content to add
    """
    try:
        with open(NOTES_FILE, 'a') as f:
            f.write(content + '\n')
        
        logger.info(f"Added note: {content}")
        return f"Added note: {content}"
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return f"Error adding note: {str(e)}"


@mcp.tool()
def delete_random_notes(count: int = 1) -> str:
    """Randomly pick and delete notes from the notes file
    
    Args:
        count: Number of notes to randomly delete (default: 1)
    """
    try:
        # Check if file exists
        if not NOTES_FILE.exists():
            return "Error: No notes file found. Nothing to delete."
        
        # Read all notes
        notes = NOTES_FILE.read_text().strip().split('\n')
        notes = [note for note in notes if note.strip()]
        
        # Check if file is empty
        if not notes:
            return "Error: Notes file is empty. Nothing to delete."
        
        # Validate count
        if count < 1:
            return "Error: Count must be at least 1."
        
        # If count exceeds available notes, delete all
        if count >= len(notes):
            deleted_notes = notes.copy()
            NOTES_FILE.write_text("")
            logger.info(f"Deleted all {len(deleted_notes)} notes")
            return f"Deleted all {len(deleted_notes)} notes:\n" + "\n".join([f"- {note}" for note in deleted_notes])
        
        # Randomly select notes to delete
        notes_to_delete = random.sample(notes, count)
        
        # Remove selected notes from the list
        remaining_notes = [note for note in notes if note not in notes_to_delete]
        
        # Write remaining notes back to file
        NOTES_FILE.write_text('\n'.join(remaining_notes) + '\n')
        
        logger.info(f"Deleted {count} random notes")
        
        # Return result
        if count == 1:
            return f"Deleted 1 random note: {notes_to_delete[0]}"
        else:
            return f"Deleted {count} random notes:\n" + "\n".join([f"- {note}" for note in notes_to_delete])
    
    except Exception as e:
        logger.error(f"Error deleting notes: {e}")
        return f"Error deleting notes: {str(e)}"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8002,
    )
