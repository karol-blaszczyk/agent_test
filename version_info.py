#!/usr/bin/env python3
"""
Version info script that outputs 'Kortex version 1.0' followed by a timestamp.
"""

from datetime import datetime

def main():
    """Main function to print version info with timestamp."""
    # Get current timestamp in YYYY-MM-DD HH:MM:SS format
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Print the version info with timestamp
    print(f"Kortex version 1.0")
    print(f"Timestamp: {timestamp}")

if __name__ == "__main__":
    main()