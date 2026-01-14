#!/usr/bin/env python3
"""
Hello World script that outputs 'Hello from Kortex' with a timestamp.
"""

from datetime import datetime

def main():
    """Main function to print greeting with timestamp."""
    # Get current timestamp in YYYY-MM-DD HH:MM:SS format
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Print the greeting with timestamp
    print(f"Hello from Kortex")
    print(f"Timestamp: {timestamp}")

if __name__ == "__main__":
    main()