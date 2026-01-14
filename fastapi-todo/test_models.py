#!/usr/bin/env python3
"""Test script to verify Todo Pydantic models and validation."""

from models import TodoBase, Todo
from pydantic import ValidationError
import sys


def test_todo_base_valid():
    """Test TodoBase with valid data."""
    print("Testing TodoBase with valid data...")
    todo = TodoBase(
        title="Buy groceries",
        description="Milk, bread, eggs, and butter",
        completed=False
    )
    assert todo.title == "Buy groceries"
    assert todo.description == "Milk, bread, eggs, and butter"
    assert todo.completed is False
    print("✅ TodoBase valid data test passed")


def test_todo_base_title_validation():
    """Test TodoBase title validation."""
    print("Testing TodoBase title validation...")
    
    # Test empty title
    try:
        TodoBase(title="", description="Valid description")
        assert False, "Should have raised ValidationError for empty title"
    except ValidationError as e:
        assert "String should have at least 1 character" in str(e)
        print("✅ Empty title validation works")
    
    # Test whitespace-only title
    try:
        TodoBase(title="   ", description="Valid description")
        assert False, "Should have raised ValidationError for whitespace title"
    except ValidationError as e:
        assert "Title cannot be empty or whitespace only" in str(e)
        print("✅ Whitespace title validation works")


def test_todo_base_description_validation():
    """Test TodoBase description validation."""
    print("Testing TodoBase description validation...")
    
    # Test empty description
    try:
        TodoBase(title="Valid title", description="")
        assert False, "Should have raised ValidationError for empty description"
    except ValidationError as e:
        assert "String should have at least 1 character" in str(e)
        print("✅ Empty description validation works")
    
    # Test whitespace-only description
    try:
        TodoBase(title="Valid title", description="   ")
        assert False, "Should have raised ValidationError for whitespace description"
    except ValidationError as e:
        assert "Description cannot be empty or whitespace only" in str(e)
        print("✅ Whitespace description validation works")


def test_todo_model():
    """Test complete Todo model with ID."""
    print("Testing Todo model with ID...")
    todo = Todo(
        id=1,
        title="Complete project",
        description="Finish the FastAPI todo application",
        completed=True
    )
    assert todo.id == 1
    assert todo.title == "Complete project"
    assert todo.description == "Finish the FastAPI todo application"
    assert todo.completed is True
    print("✅ Todo model test passed")


def test_title_stripping():
    """Test that title whitespace is stripped."""
    print("Testing title whitespace stripping...")
    todo = TodoBase(
        title="  Trimmed title  ",
        description="Valid description"
    )
    assert todo.title == "Trimmed title"
    print("✅ Title whitespace stripping works")


def test_description_stripping():
    """Test that description whitespace is stripped."""
    print("Testing description whitespace stripping...")
    todo = TodoBase(
        title="Valid title",
        description="  Trimmed description  "
    )
    assert todo.description == "Trimmed description"
    print("✅ Description whitespace stripping works")


def main():
    """Run all tests."""
    print("🧪 Testing Todo Pydantic Models")
    print("=" * 40)
    
    try:
        test_todo_base_valid()
        test_todo_base_title_validation()
        test_todo_base_description_validation()
        test_todo_model()
        test_title_stripping()
        test_description_stripping()
        
        print("=" * 40)
        print("🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())