#!/usr/bin/env python3
"""
Test script for the WeatherLogger CSV logging functionality.
"""

import os
import tempfile
from weather_logger import WeatherLogger


def test_csv_logging():
    """Test the CSV logging functionality of WeatherLogger."""
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_csv_path = temp_file.name
    
    try:
        # Create a WeatherLogger instance
        logger = WeatherLogger(temp_csv_path)
        
        print("Testing CSV logging functionality...")
        
        # Test 1: Log some temperature readings
        print("\n1. Logging temperature readings...")
        logger.log_temperature(20.0)  # 20°C
        logger.log_temperature(25.5)  # 25.5°C
        logger.log_temperature(15.3)  # 15.3°C
        print("✓ Logged 3 temperature readings")
        
        # Test 2: Verify CSV file was created and has correct structure
        print("\n2. Verifying CSV file structure...")
        assert os.path.exists(temp_csv_path), "CSV file should exist"
        
        with open(temp_csv_path, 'r') as f:
            lines = f.readlines()
        
        # Should have header + 3 data rows
        assert len(lines) == 4, f"Expected 4 lines (header + 3 data), got {len(lines)}"
        
        # Check header
        header = lines[0].strip()
        assert header == "timestamp,temperature_celsius,temperature_fahrenheit", f"Unexpected header: {header}"
        print("✓ CSV file has correct structure")
        
        # Test 3: Verify data integrity
        print("\n3. Verifying data integrity...")
        readings = logger.get_readings()
        assert len(readings) == 3, f"Expected 3 readings, got {len(readings)}"
        
        # Check first reading
        first_reading = readings[0]
        assert 'timestamp' in first_reading, "Reading should have timestamp"
        assert 'temperature_celsius' in first_reading, "Reading should have celsius temperature"
        assert 'temperature_fahrenheit' in first_reading, "Reading should have fahrenheit temperature"
        
        # Verify temperature conversion (20°C should be 68°F)
        assert abs(first_reading['temperature_celsius'] - 20.0) < 0.01, "Celsius temperature should be 20.0"
        assert abs(first_reading['temperature_fahrenheit'] - 68.0) < 0.01, "Fahrenheit temperature should be 68.0"
        print("✓ Data integrity verified")
        
        # Test 4: Test latest reading functionality
        print("\n4. Testing latest reading functionality...")
        latest = logger.get_latest_reading()
        assert latest is not None, "Should have a latest reading"
        assert latest['temperature_celsius'] == 15.3, "Latest reading should be 15.3°C"
        print("✓ Latest reading functionality works")
        
        # Test 5: Test statistics
        print("\n5. Testing statistics...")
        stats = logger.get_stats()
        assert stats['count'] == 3, "Should have 3 readings in stats"
        assert stats['min_celsius'] == 15.3, "Min celsius should be 15.3"
        assert stats['max_celsius'] == 25.5, "Max celsius should be 25.5"
        assert abs(stats['avg_celsius'] - 20.27) < 0.01, "Average should be approximately 20.27"
        print("✓ Statistics calculation works")
        
        # Test 6: Test with Fahrenheit provided
        print("\n6. Testing with Fahrenheit provided...")
        logger.log_temperature(30.0, 86.0)  # 30°C = 86°F
        readings = logger.get_readings()
        assert len(readings) == 4, "Should now have 4 readings"
        
        latest = logger.get_latest_reading()
        assert latest['temperature_celsius'] == 30.0, "Latest should be 30°C"
        assert latest['temperature_fahrenheit'] == 86.0, "Latest should be 86°F (as provided)"
        print("✓ Manual Fahrenheit input works")
        
        # Test 7: Test clear functionality
        print("\n7. Testing clear functionality...")
        logger.clear_readings()
        readings = logger.get_readings()
        assert len(readings) == 0, "Should have no readings after clear"
        
        stats = logger.get_stats()
        assert stats['count'] == 0, "Stats should show 0 count after clear"
        print("✓ Clear functionality works")
        
        print("\n🎉 All tests passed! CSV logging functionality is working correctly.")
        
    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_csv_path):
            os.unlink(temp_csv_path)


def test_file_creation_in_subdirectory():
    """Test that the logger can create files in subdirectories."""
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, "weather", "readings.csv")
        
        logger = WeatherLogger(csv_path)
        logger.log_temperature(22.0)
        
        # Verify file was created in subdirectory
        assert os.path.exists(csv_path), "CSV file should be created in subdirectory"
        
        readings = logger.get_readings()
        assert len(readings) == 1, "Should have 1 reading"
        
        print("✓ File creation in subdirectory works")


if __name__ == "__main__":
    test_csv_logging()
    test_file_creation_in_subdirectory()
    print("\nAll tests completed successfully!")