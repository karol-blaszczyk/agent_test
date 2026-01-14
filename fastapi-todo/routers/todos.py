from fastapi import APIRouter, HTTPException, Path, status
from typing import List
from models import Todo, TodoBase
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import storage
sys.path.append(str(PathLib(__file__).parent.parent.parent))
from storage import load_todos, save_todos

router = APIRouter()

@router.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos."""
    todos_data = load_todos()
    return [Todo(**todo) for todo in todos_data]

@router.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(
    todo_id: int = Path(..., description="The ID of the todo to get", ge=1)
):
    """
    Get a specific todo by ID.
    
    - **todo_id**: The ID of the todo (must be a positive integer)
    - Returns the todo if found
    - Returns 404 if todo not found
    """
    todos_data = load_todos()
    
    # Find the todo by id
    for todo_dict in todos_data:
        if todo_dict.get('id') == todo_id:
            return Todo(**todo_dict)
    
    # If not found, raise 404
    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoBase):
    """
    Create a new todo item.
    
    - **todo**: The todo data (title, description, completed)
    - Returns the created todo with generated ID
    - Returns 400 if title is empty (handled by Pydantic validation)
    """
    todos_data = load_todos()
    
    # Generate next available ID
    if todos_data:
        next_id = max(todo.get('id', 0) for todo in todos_data) + 1
    else:
        next_id = 1
    
    # Create new todo with generated ID
    new_todo = Todo(id=next_id, **todo.model_dump())
    
    # Add to todos list
    todos_data.append(new_todo.model_dump())
    
    # Save to JSON file
    save_todos(todos_data)
    
    return new_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int = Path(..., description="The ID of the todo to delete", ge=1)
):
    """
    Delete a specific todo by ID.
    
    - **todo_id**: The ID of the todo (must be a positive integer)
    - Returns 204 on successful deletion
    - Returns 404 if todo not found
    """
    todos_data = load_todos()
    
    # Find the todo by id
    for index, todo_dict in enumerate(todos_data):
        if todo_dict.get('id') == todo_id:
            # Remove the todo from the list
            todos_data.pop(index)
            save_todos(todos_data)
            return None  # Return None for 204 No Content
    
    # If not found, raise 404
    raise HTTPException(
        status_code=404,
        detail=f"Todo with id {todo_id} not found"
    )