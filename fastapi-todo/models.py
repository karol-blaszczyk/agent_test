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