from fastapi import FastAPI
from typing import List
from storage import load_todos
from pydantic import BaseModel, Field, field_validator


class TodoBase(BaseModel):
    """Base model for Todo with common fields and validation."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    completed: bool = False

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty or whitespace only."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate that description is not empty or whitespace only."""
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()


class Todo(TodoBase):
    """Complete Todo model with ID field."""
    id: int

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        str_strip_whitespace = True


app = FastAPI(
    title="Todo API",
    description="A simple todo API with FastAPI",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Welcome to Todo API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos from JSON file."""
    todos_data = load_todos()
    todos = []
    for todo_data in todos_data:
        # Ensure all required fields are present
        todo_dict = {
            "id": todo_data.get("id", 1),
            "title": todo_data.get("title", ""),
            "description": todo_data.get("description", ""),
            "completed": todo_data.get("completed", False)
        }
        todos.append(Todo(**todo_dict))
    return todos