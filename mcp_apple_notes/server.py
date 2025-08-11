import asyncio
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import Context, FastMCP

from .tools.notes_tools import NotesTools

# Initialize FastMCP server
mcp = FastMCP(name="mcp-apple-notes")

# Initialize tools
notes_tools = NotesTools()


@mcp.tool()
async def create_note(ctx: Context, name: str, body: str, folder_path: str = "Notes") -> str:
    """Create a new note with specified name and content.
    
    This unified tool handles both simple folders and nested paths.
    The folder path must exist before creating the note.
    
    Args:
        name: Name of the note (cannot be empty or contain only whitespace)
        body: Content of the note
        folder_path: Folder path (e.g., "Work" or "Work/Projects/2024"). 
                    Must exist before creating note. Defaults to "Notes".
    """
    try:
        note = await notes_tools.create_note(name, body, folder_path)
        return str(note)
    except ValueError as e:
        # Handle validation errors with clear messages
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        await ctx.error(f"Error creating note: {str(e)}")
        raise

@mcp.tool()
async def create_folder(ctx: Context, folder_name: str, folder_path: str = "") -> str:
    """Create a folder in Apple Notes.
    
    Args:
        folder_name: Name of the folder to create
        folder_path: Optional path where to create the folder (e.g., "Work/Projects"). If empty, creates at root level.
    """
    try:
        folder = await notes_tools.create_folder(folder_name, folder_path)
        return str(folder)
    except ValueError as e:
        # Handle validation errors with clear messages
        error_msg = f"Invalid input: {str(e)}"
        await ctx.error(error_msg)
        raise ValueError(error_msg)
    except RuntimeError as e:
        # Handle AppleScript errors with helpful context
        error_msg = str(e)
        await ctx.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error creating folder '{folder_name}' in path '{folder_path}': {str(e)}"
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def read_note_by_name(ctx: Context, note_name: str, folder_name: str) -> str:
    """Read all notes with the given name in the specified folder."""
    try:
        notes = await notes_tools.read_note_by_name(note_name, folder_name)
        
        if not notes:
            return f"No notes found with name '{note_name}' in folder '{folder_name}'"
        
        if len(notes) == 1:
            return f"Found 1 note:\n{str(notes[0])}"
        else:
            result = f"Found {len(notes)} notes with name '{note_name}' in folder '{folder_name}':\n"
            for i, note in enumerate(notes, 1):
                result += f"\n--- Note {i} ---\n"
                result += f"Creation Date: {note['creation_date']}\n"
                result += f"Modification Date: {note['modification_date']}\n"
                result += f"Content:\n{note['body']}\n"
            return result
            
    except Exception as e:
        await ctx.error(f"Error reading note: {str(e)}")
        raise

@mcp.tool()
async def read_note_by_name_in_path(ctx: Context, note_name: str, folder_path: str) -> str:
    """Read all notes with the given name in the specified folder path."""
    try:
        notes = await notes_tools.read_note_by_name_in_path(note_name, folder_path)
        
        if not notes:
            return f"No notes found with name '{note_name}' in folder path '{folder_path}'"
        
        if len(notes) == 1:
            return f"Found 1 note:\n{str(notes[0])}"
        else:
            result = f"Found {len(notes)} notes with name '{note_name}' in folder path '{folder_path}':\n"
            for i, note in enumerate(notes, 1):
                result += f"\n--- Note {i} ---\n"
                result += f"Creation Date: {note['creation_date']}\n"
                result += f"Modification Date: {note['modification_date']}\n"
                result += f"Content:\n{note['body']}\n"
            return result
            
    except Exception as e:
        await ctx.error(f"Error reading note by path: {str(e)}")
        raise



@mcp.tool()
async def get_folder_details(ctx: Context, folder_name: str) -> str:
    """Get comprehensive details about a folder including all subfolders and notes in hierarchy."""
    try:
        folder_details = await notes_tools.get_folder_details(folder_name)
        
        # Format the response in a readable way
        result = f"📁 Folder Details: {folder_name}\n"
        result += f"📂 Path: {folder_details.get('path', 'N/A')}\n"
        result += f"📝 Total Notes: {folder_details.get('total_notes', 0)}\n"
        result += f"📁 Total Subfolders: {folder_details.get('total_subfolders', 0)}\n\n"
        
        # Add notes information
        notes = folder_details.get('notes', [])
        if notes:
            result += "📝 Notes:\n"
            for i, note in enumerate(notes, 1):
                result += f"  {i}. {note.get('name', 'N/A')}\n"
                result += f"     Created: {note.get('creation_date', 'N/A')}\n"
                result += f"     Modified: {note.get('modification_date', 'N/A')}\n"
                if note.get('body'):
                    result += f"     Content: {note.get('body', '')[:100]}...\n"
                result += "\n"
        else:
            result += "📝 Notes: None\n\n"
        
        # Add subfolders information
        subfolders = folder_details.get('subfolders', [])
        if subfolders:
            result += "📁 Subfolders:\n"
            for i, subfolder in enumerate(subfolders, 1):
                result += f"  {i}. {subfolder.get('name', 'N/A')} (Path: {subfolder.get('path', 'N/A')})\n"
                result += f"     Notes: {subfolder.get('total_notes', 0)}, Subfolders: {subfolder.get('total_subfolders', 0)}\n\n"
        else:
            result += "📁 Subfolders: None\n\n"
        
        return result
    except Exception as e:
        await ctx.error(f"Error getting folder details: {str(e)}")
        raise

@mcp.tool()
async def rename_folder(ctx: Context, folder_path: str, current_name: str, new_name: str) -> str:
    """Rename a folder in Apple Notes."""
    try:
        rename_result = await notes_tools.rename_folder(folder_path, current_name, new_name)
        
        # Format the response
        result = f"🔄 Folder Rename Result:\n"
        result += f"📂 Path: {rename_result.get('folder_path', 'N/A')}\n"
        result += f"📝 Old Name: {rename_result.get('current_name', 'N/A')}\n"
        result += f"📝 New Name: {rename_result.get('new_name', 'N/A')}\n"
        result += f"✅ Status: {rename_result.get('status', 'N/A')}\n"
        result += f"💬 Message: {rename_result.get('message', 'N/A')}\n"
        
        return result
    except Exception as e:
        await ctx.error(f"Error renaming folder: {str(e)}")
        raise

@mcp.tool()
async def move_folder(ctx: Context, source_path: str, folder_name: str, target_path: str = "") -> str:
    """Move a folder from one location to another in Apple Notes."""
    try:
        move_result = await notes_tools.move_folder(source_path, folder_name, target_path)
        
        # Format the response
        result = f"📦 Folder Move Result:\n"
        result += f"📁 Folder Name: {move_result.get('folder_name', 'N/A')}\n"
        result += f"📂 Source Path: {move_result.get('source_path', 'N/A')}\n"
        result += f"📂 Target Path: {move_result.get('target_path', 'N/A')}\n"
        result += f"✅ Status: {move_result.get('status', 'N/A')}\n"
        result += f"💬 Message: {move_result.get('message', 'N/A')}\n"
        
        return result
    except Exception as e:
        await ctx.error(f"Error moving folder: {str(e)}")
        raise

@mcp.tool()
async def list_folder_with_structure(ctx: Context) -> str:
    """List the complete folder structure with hierarchical tree format."""
    try:
        folder_structure = await notes_tools.list_folder_with_structure()
        
        if not folder_structure:
            return "No folders found in Apple Notes"
        
        # Return filtered AppleScript result
        return f"📁 Apple Notes Folder Structure:\n\n{folder_structure}"
    except Exception as e:
        await ctx.error(f"Error listing folder structure: {str(e)}")
        raise

@mcp.tool()
async def list_notes_with_structure(ctx: Context) -> str:
    """List the complete folder structure with notes included in hierarchical tree format."""
    try:
        notes_structure = await notes_tools.list_notes_with_structure()
        
        if not notes_structure:
            return "No folders or notes found in Apple Notes"
        
        # Return filtered AppleScript result
        return f"📁 Apple Notes Structure with Notes:\n\n{notes_structure}"
    except Exception as e:
        await ctx.error(f"Error listing notes structure: {str(e)}")
        raise

# Run the server
if __name__ == "__main__":
    mcp.run()
