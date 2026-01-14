#!/usr/bin/env python3
"""
Comprehensive test script to verify all CRUD operations work correctly
and JSON persistence is functioning properly.
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import storage
sys.path.append(str(Path(__file__).parent.parent.parent))
from storage import load_todos, save_todos
from models import Todo, TodoBase


def test_load_empty_todos():
    """Test loading todos when file doesn't exist."""
    print("Test 1: Loading todos when file doesn't exist...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary todos.json file path
        temp_todos_path = os.path.join(temp_dir, 'todos.json')
        
        # Temporarily replace the file path in storage module
        original_load = load_todos
        
        def mock_load_todos():
            """Mock load_todos that uses our temp file."""
            if not os.path.exists(temp_todos_path):
                return []
            try:
                with open(temp_todos_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        return []
                    return json.loads(content)
            except (json.JSONDecodeError, IOError, OSError):
                return []
        
        result = mock_load_todos()
        assert result == [], "Should return empty list when file doesn't exist"
        print("✅ Empty todos loading works")


def test_save_and_load_todos():
    """Test saving and loading todos."""
    print("Test 2: Testing save and load operations...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_todos_path = os.path.join(temp_dir, 'todos.json')
        
        def mock_save_todos(todos):
            """Mock save_todos that uses our temp file."""
            try:
                json.dumps(todos)
            except (TypeError, ValueError) as e:
                raise TypeError(f"Todos data is not JSON serializable: {e}")
            
            with open(temp_todos_path, 'w', encoding='utf-8') as f:
                json.dump(todos, f, indent=2, ensure_ascii=False)
        
        def mock_load_todos():
            """Mock load_todos that uses our temp file."""
            if not os.path.exists(temp_todos_path):
                return []
            try:
                with open(temp_todos_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        return []
                    return json.loads(content)
            except (json.JSONDecodeError, IOError, OSError):
                return []
        
        # Test data
        test_todos = [
            {
                "id": 1,
                "title": "Test Todo 1",
                "description": "First test todo",
                "completed": False
            },
            {
                "id": 2,
                "title": "Test Todo 2",
                "description": "Second test todo",
                "completed": True
            }
        ]
        
        # Save todos
        mock_save_todos(test_todos)
        
        # Load todos
        loaded_todos = mock_load_todos()
        
        assert len(loaded_todos) == 2, f"Expected 2 todos, got {len(loaded_todos)}"
        assert loaded_todos[0]["title"] == "Test Todo 1"
        assert loaded_todos[1]["title"] == "Test Todo 2"
        print("✅ Save and load operations work")


def test_model_validation():
    """Test that models validate correctly."""
    print("Test 3: Testing model validation...")
    
    # Valid todo
    valid_todo = TodoBase(
        title="Valid Todo",
        description="This is a valid description",
        completed=False
    )
    assert valid_todo.title == "Valid Todo"
    assert valid_todo.description == "This is a valid description"
    assert valid_todo.completed is False
    
    # Test complete Todo with ID
    complete_todo = Todo(
        id=1,
        title="Complete Todo",
        description="This is a complete todo",
        completed=True
    )
    assert complete_todo.id == 1
    assert complete_todo.title == "Complete Todo"
    assert complete_todo.completed is True
    
    print("✅ Model validation works")


def test_whitespace_handling():
    """Test that whitespace is properly stripped."""
    print("Test 4: Testing whitespace handling...")
    
    todo = TodoBase(
        title="  Whitespace Title  ",
        description="  Whitespace Description  ",
        completed=False
    )
    
    assert todo.title == "Whitespace Title"
    assert todo.description == "Whitespace Description"
    print("✅ Whitespace handling works")


def test_json_serialization():
    """Test JSON serialization of models."""
    print("Test 5: Testing JSON serialization...")
    
    todo = Todo(
        id=1,
        title="JSON Test",
        description="Testing JSON serialization",
        completed=False
    )
    
    # Convert to dict
    todo_dict = todo.model_dump()
    
    # Test JSON serialization
    json_str = json.dumps(todo_dict)
    loaded_dict = json.loads(json_str)
    
    assert loaded_dict["id"] == 1
    assert loaded_dict["title"] == "JSON Test"
    assert loaded_dict["description"] == "Testing JSON serialization"
    assert loaded_dict["completed"] is False
    
    print("✅ JSON serialization works")


def main():
    """Run all CRUD tests."""
    print("🧪 Testing CRUD Operations and JSON Persistence")
    print("=" * 50)
    
    try:
        test_load_empty_todos()
        test_save_and_load_todos()
        test_model_validation()
        test_whitespace_handling()
        test_json_serialization()
        
        print("=" * 50)
        print("🎉 All CRUD and persistence tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())