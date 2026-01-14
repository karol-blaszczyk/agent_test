"""
Comprehensive test suite for FastAPI Todo application.

Tests all endpoints with pytest-asyncio and httpx.AsyncClient.
Includes setup/teardown for clean state management.
"""

import pytest
import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the FastAPI app
from main import app


@pytest.fixture
def temp_todos_file():
    """
    Create a temporary todos.json file for testing.
    
    Yields:
        Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_path = f.name
    
    # Monkey patch the storage module to use our temp file
    import storage
    original_load = storage.load_todos
    original_save = storage.save_todos
    
    def load_todos() -> List[Dict[str, Any]]:
        """Load todos from temp file."""
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_todos(todos: List[Dict[str, Any]]) -> None:
        """Save todos to temp file."""
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)
    
    # Apply monkey patches
    storage.load_todos = load_todos
    storage.save_todos = save_todos
    
    yield temp_path
    
    # Cleanup
    storage.load_todos = original_load
    storage.save_todos = original_save
    
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
async def async_client():
    """
    Create an async test client for the FastAPI app.
    
    Yields:
        AsyncClient instance
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_todo_data():
    """
    Provide sample todo data for testing.
    
    Returns:
        Dict containing sample todo data
    """
    return {
        "title": "Test Todo",
        "description": "This is a test todo item",
        "completed": False
    }


@pytest.fixture
def sample_todos():
    """
    Provide multiple sample todos for testing.
    
    Returns:
        List of sample todo dictionaries
    """
    return [
        {
            "title": "First Todo",
            "description": "Description for first todo",
            "completed": False
        },
        {
            "title": "Second Todo", 
            "description": "Description for second todo",
            "completed": True
        },
        {
            "title": "Third Todo",
            "description": "Description for third todo", 
            "completed": False
        }
    ]


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test the root welcome endpoint."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Todo API"
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test the health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestGetTodos:
    """Test GET /api/todos endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_todos_empty(self, async_client, temp_todos_file):
        """Test getting todos when none exist."""
        response = await async_client.get("/api/todos")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_todos_with_data(self, async_client, temp_todos_file, sample_todos):
        """Test getting todos when data exists."""
        # Pre-populate the todos file
        import storage
        
        # Create todos with proper IDs
        todos_data = []
        for i, todo_data in enumerate(sample_todos, 1):
            todo_dict = todo_data.copy()
            todo_dict["id"] = i
            todos_data.append(todo_dict)
        
        storage.save_todos(todos_data)
        
        response = await async_client.get("/api/todos")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(sample_todos)
        
        # Verify first todo
        first_todo = data[0]
        assert first_todo["title"] == sample_todos[0]["title"]
        assert first_todo["description"] == sample_todos[0]["description"]
        assert first_todo["completed"] == sample_todos[0]["completed"]
        assert first_todo["id"] == 1


class TestGetTodoById:
    """Test GET /api/todos/{todo_id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_todo_by_id_exists(self, async_client, temp_todos_file, sample_todo_data):
        """Test getting a todo that exists."""
        import storage
        
        # Create a todo
        todo_dict = sample_todo_data.copy()
        todo_dict["id"] = 1
        storage.save_todos([todo_dict])
        
        response = await async_client.get("/api/todos/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["completed"] == sample_todo_data["completed"]
        assert data["id"] == 1
    
    @pytest.mark.asyncio
    async def test_get_todo_by_id_not_found(self, async_client, temp_todos_file):
        """Test getting a todo that doesn't exist."""
        response = await async_client.get("/api/todos/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Todo with id 999 not found" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_todo_by_invalid_id(self, async_client, temp_todos_file):
        """Test getting a todo with invalid ID format."""
        response = await async_client.get("/api/todos/invalid")
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]


class TestCreateTodo:
    """Test POST /api/todos endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_todo_success(self, async_client, temp_todos_file, sample_todo_data):
        """Test creating a todo successfully."""
        response = await async_client.post("/api/todos", json=sample_todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["completed"] == sample_todo_data["completed"]
        assert data["id"] == 1  # First todo should have ID 1
        
        # Verify it was actually saved
        import storage
        saved_todos = storage.load_todos()
        assert len(saved_todos) == 1
        assert saved_todos[0]["title"] == sample_todo_data["title"]
    
    @pytest.mark.asyncio
    async def test_create_todo_with_empty_title(self, async_client, temp_todos_file):
        """Test creating a todo with empty title."""
        todo_data = {
            "title": "",
            "description": "Valid description"
        }
        
        response = await async_client.post("/api/todos", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_todo_with_whitespace_title(self, async_client, temp_todos_file):
        """Test creating a todo with whitespace-only title."""
        todo_data = {
            "title": "   ",
            "description": "Valid description"
        }
        
        response = await async_client.post("/api/todos", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_todo_with_empty_description(self, async_client, temp_todos_file):
        """Test creating a todo with empty description."""
        todo_data = {
            "title": "Valid Title",
            "description": ""
        }
        
        response = await async_client.post("/api/todos", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_multiple_todos(self, async_client, temp_todos_file, sample_todos):
        """Test creating multiple todos."""
        created_todos = []
        
        for i, todo_data in enumerate(sample_todos):
            response = await async_client.post("/api/todos", json=todo_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == i + 1
            created_todos.append(data)
        
        # Verify all todos were created
        import storage
        saved_todos = storage.load_todos()
        assert len(saved_todos) == len(sample_todos)


class TestDeleteTodo:
    """Test DELETE /api/todos/{todo_id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_todo_success(self, async_client, temp_todos_file, sample_todo_data):
        """Test deleting a todo successfully."""
        import storage
        
        # Create a todo first
        todo_dict = sample_todo_data.copy()
        todo_dict["id"] = 1
        storage.save_todos([todo_dict])
        
        # Delete the todo
        response = await async_client.delete("/api/todos/1")
        
        assert response.status_code == 204
        
        # Verify it was actually deleted
        saved_todos = storage.load_todos()
        assert len(saved_todos) == 0
    
    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, async_client, temp_todos_file):
        """Test deleting a todo that doesn't exist."""
        response = await async_client.delete("/api/todos/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Todo with id 999 not found" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_todo_multiple(self, async_client, temp_todos_file, sample_todos):
        """Test deleting from multiple todos."""
        import storage
        
        # Create multiple todos
        todos_data = []
        for i, todo_data in enumerate(sample_todos, 1):
            todo_dict = todo_data.copy()
            todo_dict["id"] = i
            todos_data.append(todo_dict)
        
        storage.save_todos(todos_data)
        
        # Delete the middle todo (ID 2)
        response = await async_client.delete("/api/todos/2")
        assert response.status_code == 204
        
        # Verify only 2 todos remain
        saved_todos = storage.load_todos()
        assert len(saved_todos) == 2
        
        # Verify the correct todo was deleted
        remaining_ids = [todo["id"] for todo in saved_todos]
        assert 2 not in remaining_ids
        assert 1 in remaining_ids
        assert 3 in remaining_ids


class TestValidationErrors:
    """Test various validation error scenarios."""
    
    @pytest.mark.asyncio
    async def test_validation_error_format(self, async_client, temp_todos_file):
        """Test that validation errors have proper format."""
        # Test with invalid data that should trigger Pydantic validation
        invalid_data = {
            "title": "Valid Title"
            # Missing required description
        }
        
        response = await async_client.post("/api/todos", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]
        assert "errors" in data
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0
        
        # Check error structure
        error = data["errors"][0]
        assert "loc" in error  # location of error
        assert "msg" in error  # error message
        assert "type" in error  # error type
    
    @pytest.mark.asyncio
    async def test_title_too_long(self, async_client, temp_todos_file):
        """Test creating a todo with title exceeding max length."""
        todo_data = {
            "title": "A" * 300,  # Exceeds 255 character limit
            "description": "Valid description"
        }
        
        response = await async_client.post("/api/todos", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Validation error" in data["detail"]


class TestConcurrentOperations:
    """Test concurrent operations to ensure thread safety."""
    
    @pytest.mark.asyncio
    async def test_concurrent_create_todos(self, async_client, temp_todos_file, sample_todos):
        """Test creating multiple todos concurrently."""
        # Create multiple todos concurrently
        tasks = []
        for todo_data in sample_todos:
            task = async_client.post("/api/todos", json=todo_data)
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 201
        
        # Verify all todos were created with unique IDs
        import storage
        saved_todos = storage.load_todos()
        assert len(saved_todos) == len(sample_todos)
        
        # Verify IDs are unique and sequential
        ids = [todo["id"] for todo in saved_todos]
        assert len(set(ids)) == len(ids)  # All unique
        assert min(ids) == 1
        assert max(ids) == len(sample_todos)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])