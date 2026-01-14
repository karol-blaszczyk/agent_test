#!/usr/bin/env python3
"""
Verification script to check hello_world.py output and timestamp validity.
"""

import subprocess
import re
from datetime import datetime

def verify_hello_world():
    """Run hello_world.py and verify its output."""
    try:
        # Run the hello_world.py script
        result = subprocess.run(['python', 'hello_world.py'], 
                              capture_output=True, text=True, cwd='/app/workspaces/cb0b7346-6c7d-4e2a-8eaf-38e41603327d')
        
        if result.returncode != 0:
            print(f"❌ Script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        
        output_lines = result.stdout.strip().split('\n')
        
        # Check first line
        if len(output_lines) < 1 or output_lines[0] != "Hello from Kortex":
            print(f"❌ First line should be 'Hello from Kortex', got: {output_lines[0] if output_lines else 'empty'}")
            return False
        
        # Check second line for timestamp
        if len(output_lines) < 2:
            print("❌ Missing timestamp line")
            return False
        
        timestamp_line = output_lines[1]
        timestamp_match = re.match(r'Timestamp: (.+)', timestamp_line)
        
        if not timestamp_match:
            print(f"❌ Timestamp line format incorrect: {timestamp_line}")
            return False
        
        timestamp_str = timestamp_match.group(1)
        
        # Parse the timestamp
        try:
            script_time = datetime.fromisoformat(timestamp_str)
        except ValueError as e:
            print(f"❌ Invalid timestamp format: {timestamp_str}")
            print(f"Error: {e}")
            return False
        
        # Check if timestamp is recent (within last minute)
        current_time = datetime.now()
        time_diff = (current_time - script_time).total_seconds()
        
        if abs(time_diff) > 60:  # More than 60 seconds difference
            print(f"❌ Timestamp is not recent. Difference: {time_diff} seconds")
            return False
        
        print("✅ All checks passed!")
        print(f"✅ Output: 'Hello from Kortex'")
        print(f"✅ Timestamp: {timestamp_str}")
        print(f"✅ Timestamp is recent (within last minute)")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_hello_world()
    exit(0 if success else 1)