#!/usr/bin/env python3
"""
Test script for Flask application routes and functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_flask_app():
    """Test all Flask app routes and functionality"""
    
    # Create test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    print("🧪 Testing Flask Application...")
    
    # Test 1: Home page
    print("\n1. Testing home page...")
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Home page loads successfully")
    else:
        print(f"   ❌ Home page failed: {response.status_code}")
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    response = client.get('/health')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Health endpoint works")
    else:
        print(f"   ❌ Health endpoint failed: {response.status_code}")
    
    # Test 3: Run hello_world.py script
    print("\n3. Testing script execution (hello_world.py)...")
    response = client.get('/run/hello_world.py')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Script execution works")
        print(f"   Response preview: {response.get_data(as_text=True)[:100]}...")
    else:
        print(f"   ❌ Script execution failed: {response.status_code}")
    
    # Test 4: View hello_world.py script
    print("\n4. Testing script viewing (hello_world.py)...")
    response = client.get('/view/hello_world.py')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Script viewing works")
    else:
        print(f"   ❌ Script viewing failed: {response.status_code}")
    
    # Test 5: Run verify_hello_world.py script
    print("\n5. Testing verify_hello_world.py execution...")
    response = client.get('/run/verify_hello_world.py')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Verify script execution works")
    else:
        print(f"   ❌ Verify script execution failed: {response.status_code}")
    
    # Test 6: View verify_hello_world.py script
    print("\n6. Testing verify_hello_world.py viewing...")
    response = client.get('/view/verify_hello_world.py')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Verify script viewing works")
    else:
        print(f"   ❌ Verify script viewing failed: {response.status_code}")
    
    # Test 7: Non-existent script
    print("\n7. Testing error handling for non-existent script...")
    response = client.get('/run/nonexistent.py')
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        print("   ✅ Error handling works (404 for non-existent script)")
    else:
        print(f"   ❌ Error handling failed: {response.status_code}")
    
    print("\n🎯 Flask Application Testing Complete!")
    return True

if __name__ == "__main__":
    try:
        test_flask_app()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)