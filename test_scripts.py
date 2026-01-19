#!/usr/bin/env python3
"""
Test script to verify the /scripts endpoint works correctly.
"""

import sys
import os
sys.path.append('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')

# Change to the workspace directory
os.chdir('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')

import app

def test_scripts_endpoint():
    """Test the /scripts endpoint."""
    try:
        with app.app.test_client() as client:
            response = client.get('/scripts')
            print(f'Status Code: {response.status_code}')
            print(f'Content Type: {response.content_type}')
            
            if response.status_code == 200:
                print('SUCCESS: /scripts endpoint is working!')
                print(f'Response length: {len(response.data)} bytes')
                
                # Check if the response contains expected content
                html_content = response.data.decode('utf-8')
                if 'Available Scripts' in html_content:
                    print('✓ Page title found')
                if 'Run Script' in html_content:
                    print('✓ Script cards with run buttons found')
                if 'View Code' in html_content:
                    print('✓ View code buttons found')
                    
                return True
            else:
                print(f'ERROR: Status code {response.status_code}')
                print(f'Response: {response.data.decode("utf-8")[:200]}...')
                return False
                
    except Exception as e:
        print(f'ERROR: Exception occurred: {e}')
        return False

if __name__ == '__main__':
    print('Testing /scripts endpoint...')
    success = test_scripts_endpoint()
    sys.exit(0 if success else 1)