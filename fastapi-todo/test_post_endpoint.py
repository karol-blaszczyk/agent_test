#!/usr/bin/env python3
"""
Test script for the POST /todos endpoint
"""

import json
import requests
import sys

def test_post_todos():
    """Test the POST /todos endpoint"""
    base_url = "http://localhost:8000/api"
    
    # Test 1: Valid todo
    print("Test 1: Creating valid todo...")
    valid_todo = {
        "title": "Test Todo",
        "description": "This is a test todo",
        "completed": False
    }
    
    try:
        response = requests.post(f"{base_url}/todos", json=valid_todo)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            created_todo = response.json()
            print(f"✅ Created todo with ID: {created_todo['id']}")
        else:
            print(f"❌ Failed to create todo")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Empty title validation
    print("\nTest 2: Testing empty title validation...")
    invalid_todo = {
        "title": "",
        "description": "This should fail",
        "completed": False
    }
    
    try:
        response = requests.post(f"{base_url}/todos", json=invalid_todo)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Empty title validation works (422 status)")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Whitespace-only title validation
    print("\nTest 3: Testing whitespace-only title validation...")
    whitespace_todo = {
        "title": "   ",
        "description": "This should also fail",
        "completed": False
    }
    
    try:
        response = requests.post(f"{base_url}/todos", json=whitespace_todo)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Whitespace title validation works (422 status)")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Get all todos to verify storage
    print("\nTest 4: Getting all todos...")
    try:
        response = requests.get(f"{base_url}/todos")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            todos = response.json()
            print(f"✅ Found {len(todos)} todos")
            for todo in todos:
                print(f"  - ID {todo['id']}: {todo['title']}")
        else:
            print(f"❌ Failed to get todos")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_post_todos()
    sys.exit(0 if success else 1)