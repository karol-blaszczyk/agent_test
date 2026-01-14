"""
JSON storage utility functions for todo management.

This module provides atomic file operations for reading and writing
todo items to a JSON file with proper error handling.
"""

import json
import os
import tempfile
from typing import Any, Dict, List


def load_todos() -> List[Dict[str, Any]]:
    """
    Load todos from todos.json file.
    
    Returns an empty list if the file doesn't exist or is invalid.
    
    Returns:
        List of todo dictionaries. Returns empty list if file doesn't exist.
    """
    print(f"DEBUG: Loading todos from {os.path.abspath('../todos.json')}")
    if not os.path.exists('../todos.json'):
        print("DEBUG: todos.json does not exist, returning empty list")
        return []
    
    try:
        with open('../todos.json', 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                print("DEBUG: todos.json is empty, returning empty list")
                return []
            todos = json.loads(content)
            print(f"DEBUG: Loaded {len(todos)} todos from file")
            return todos
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"DEBUG: Error loading todos: {e}")
        return []


def save_todos(todos: List[Dict[str, Any]]) -> None:
    """
    Save todos to todos.json file atomically.
    
    Writes to a temporary file first, then renames it to ensure
    atomic operations and prevent data corruption.
    
    Args:
        todos: List of todo dictionaries to save.
    
    Raises:
        IOError: If unable to write to the temporary file or rename it.
        TypeError: If todos is not JSON serializable.
    """
    print(f"DEBUG: Saving {len(todos)} todos to file")
    
    # Validate that todos is JSON serializable
    try:
        json.dumps(todos)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Todos data is not JSON serializable: {e}")
    
    # Create temporary file in same directory for atomic rename
    temp_fd = None
    temp_path = None
    
    try:
        # Create temporary file in same directory as target
        temp_fd, temp_path = tempfile.mkstemp(
            dir='..',
            prefix='todos_',
            suffix='.tmp'
        )
        
        # Write data to temporary file
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)
        
        # Atomic rename from temp to final file
        os.replace(temp_path, '../todos.json')
        temp_path = None  # Prevent cleanup of renamed file
        print(f"DEBUG: Successfully saved {len(todos)} todos to file")
        
    except Exception as e:
        print(f"DEBUG: Error saving todos: {e}")
        # Clean up temporary file on error
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # Best effort cleanup
        raise
    finally:
        # Close file descriptor if still open (shouldn't happen with fdopen)
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except OSError:
                pass