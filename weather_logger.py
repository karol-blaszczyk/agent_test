#!/usr/bin/env python3
"""
Weather Logger with CSV logging functionality.

This module provides functionality to log temperature readings to a CSV file
with timestamps, creating the file if it doesn't exist.
"""

import csv
import datetime
import os
import random
from pathlib import Path
from typing import Optional, Union, Dict, Any


class WeatherLogger:
    """
    A weather logger that records temperature readings to a CSV file.
    """
    
    def __init__(self, csv_file_path: Union[str, Path] = "temperature_readings.csv"):
        """
        Initialize the WeatherLogger.
        
        Args:
            csv_file_path: Path to the CSV file for storing temperature readings.
                         Defaults to "temperature_readings.csv" in the current directory.
        """
        self.csv_file_path = Path(csv_file_path)
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self) -> None:
        """
        Ensure the CSV file exists, creating it with headers if it doesn't.
        """
        if not self.csv_file_path.exists() or self.csv_file_path.stat().st_size == 0:
            self.csv_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'temperature_celsius', 'temperature_fahrenheit'])
    
    def log_temperature(self, temperature_celsius: float, temperature_fahrenheit: Optional[float] = None) -> None:
        """
        Log a temperature reading to the CSV file with timestamp.
        
        Args:
            temperature_celsius: Temperature in Celsius degrees.
            temperature_fahrenheit: Temperature in Fahrenheit degrees. If not provided,
                                   it will be calculated from Celsius.
        """
        if temperature_fahrenheit is None:
            temperature_fahrenheit = self._celsius_to_fahrenheit(temperature_celsius)
        
        timestamp = datetime.datetime.now().isoformat()
        
        with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, temperature_celsius, temperature_fahrenheit])
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """
        Convert Celsius to Fahrenheit.
        
        Args:
            celsius: Temperature in Celsius.
            
        Returns:
            Temperature in Fahrenheit.
        """
        return (celsius * 9/5) + 32
    
    def get_readings(self, limit: Optional[int] = None) -> list[dict]:
        """
        Retrieve temperature readings from the CSV file.
        
        Args:
            limit: Maximum number of readings to return. If None, all readings are returned.
                  
        Returns:
            List of dictionaries containing temperature readings.
        """
        readings = []
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                readings.append({
                    'timestamp': row['timestamp'],
                    'temperature_celsius': float(row['temperature_celsius']),
                    'temperature_fahrenheit': float(row['temperature_fahrenheit'])
                })
        
        if limit is not None:
            readings = readings[-limit:]
        
        return readings
    
    def get_latest_reading(self) -> Optional[dict]:
        """
        Get the most recent temperature reading.
        
        Returns:
            Dictionary containing the latest reading, or None if no readings exist.
        """
        readings = self.get_readings(limit=1)
        return readings[0] if readings else None
    
    def clear_readings(self) -> None:
        """
        Clear all temperature readings from the CSV file.
        """
        with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'temperature_celsius', 'temperature_fahrenheit'])
    
    def get_stats(self) -> dict:
        """
        Get basic statistics about the temperature readings.
        
        Returns:
            Dictionary containing statistics (count, min, max, avg temperatures).
        """
        readings = self.get_readings()
        
        if not readings:
            return {
                'count': 0,
                'min_celsius': None,
                'max_celsius': None,
                'avg_celsius': None,
                'min_fahrenheit': None,
                'max_fahrenheit': None,
                'avg_fahrenheit': None
            }
        
        celsius_temps = [r['temperature_celsius'] for r in readings]
        fahrenheit_temps = [r['temperature_fahrenheit'] for r in readings]
        
        return {
            'count': len(readings),
            'min_celsius': min(celsius_temps),
            'max_celsius': max(celsius_temps),
            'avg_celsius': sum(celsius_temps) / len(celsius_temps),
            'min_fahrenheit': min(fahrenheit_temps),
            'max_fahrenheit': max(fahrenheit_temps),
            'avg_fahrenheit': sum(fahrenheit_temps) / len(fahrenheit_temps)
        }
    
    def fetch_and_log_weather(self, location: str = "New York") -> Dict[str, Any]:
        """
        Fetch weather data from the mock API and log the temperature.
        
        This method uses the mock weather API to get current weather data
        and automatically logs the temperature to the CSV file.
        
        Args:
            location: The location for which to fetch weather data.
                     Defaults to "New York".
        
        Returns:
            Dictionary containing the weather data that was fetched.
        """
        # Fetch weather data from mock API
        weather_data = mock_weather_api(location)
        
        # Log the current temperature
        self.log_temperature(
            weather_data["current_temperature_celsius"],
            weather_data["current_temperature_fahrenheit"]
        )
        
        return weather_data


def mock_weather_api(location: str = "New York") -> Dict[str, Any]:
    """
    Simulate fetching weather data from a mock API that returns random temperature data.
    
    This function simulates what a real weather API might return, including:
    - Current temperature (random but realistic for the location)
    - Feels-like temperature
    - Humidity and wind speed
    - Weather conditions
    - Location information
    
    Args:
        location: The location for which to fetch weather data. Defaults to "New York".
                 This parameter is used to make the mock more realistic.
    
    Returns:
        Dictionary containing mock weather data with the following structure:
        {
            "location": str,
            "current_temperature_celsius": float,
            "current_temperature_fahrenheit": float,
            "feels_like_celsius": float,
            "feels_like_fahrenheit": float,
            "humidity_percent": int,
            "wind_speed_kmh": float,
            "weather_condition": str,
            "timestamp": str (ISO format),
            "api_response_time_ms": int
        }
    """
    # Base temperature ranges for different locations (in Celsius)
    location_temperatures = {
        "New York": (5, 25),
        "London": (2, 20),
        "Tokyo": (10, 30),
        "Sydney": (15, 35),
        "Moscow": (-15, 5),
        "Miami": (20, 35),
        "Seattle": (5, 22),
        "Denver": (-5, 28)
    }
    
    # Get temperature range for location, default to moderate range
    temp_range = location_temperatures.get(location, (0, 25))
    
    # Generate random current temperature within range
    current_temp_celsius = random.uniform(temp_range[0], temp_range[1])
    current_temp_fahrenheit = (current_temp_celsius * 9/5) + 32
    
    # Generate feels-like temperature (slightly different from actual)
    feels_like_offset = random.uniform(-3, 3)  # Feels like can be different
    feels_like_celsius = current_temp_celsius + feels_like_offset
    feels_like_fahrenheit = (feels_like_celsius * 9/5) + 32
    
    # Generate other weather parameters
    humidity_percent = random.randint(30, 90)  # Realistic humidity range
    wind_speed_kmh = random.uniform(0, 50)  # 0-50 km/h wind speed
    
    # Weather conditions based on temperature and random selection
    if current_temp_celsius < 0:
        conditions = ["Snow", "Cloudy", "Clear"]
        weights = [0.4, 0.4, 0.2]
    elif current_temp_celsius < 10:
        conditions = ["Cloudy", "Rain", "Clear", "Fog"]
        weights = [0.4, 0.3, 0.2, 0.1]
    elif current_temp_celsius < 25:
        conditions = ["Clear", "Partly Cloudy", "Cloudy", "Rain"]
        weights = [0.5, 0.3, 0.15, 0.05]
    else:
        conditions = ["Clear", "Partly Cloudy", "Hot", "Humid"]
        weights = [0.6, 0.25, 0.1, 0.05]
    
    weather_condition = random.choices(conditions, weights=weights)[0]
    
    # Simulate API response time (50-500ms)
    api_response_time_ms = random.randint(50, 500)
    
    return {
        "location": location,
        "current_temperature_celsius": round(current_temp_celsius, 1),
        "current_temperature_fahrenheit": round(current_temp_fahrenheit, 1),
        "feels_like_celsius": round(feels_like_celsius, 1),
        "feels_like_fahrenheit": round(feels_like_fahrenheit, 1),
        "humidity_percent": humidity_percent,
        "wind_speed_kmh": round(wind_speed_kmh, 1),
        "weather_condition": weather_condition,
        "timestamp": datetime.datetime.now().isoformat(),
        "api_response_time_ms": api_response_time_ms
    }


def main():
    """
    Example usage of the WeatherLogger class with mock API functionality.
    """
    # Create a weather logger
    logger = WeatherLogger("weather_data.csv")
    
    print("=== Weather Logger with Mock API Demo ===\n")
    
    # Demo 1: Use the mock API to fetch and log weather data
    print("1. Fetching weather data from mock API...")
    weather_data = logger.fetch_and_log_weather("New York")
    print(f"   Location: {weather_data['location']}")
    print(f"   Temperature: {weather_data['current_temperature_celsius']}°C ({weather_data['current_temperature_fahrenheit']}°F)")
    print(f"   Condition: {weather_data['weather_condition']}")
    print(f"   Humidity: {weather_data['humidity_percent']}%")
    print(f"   Wind Speed: {weather_data['wind_speed_kmh']} km/h")
    print(f"   API Response Time: {weather_data['api_response_time_ms']}ms")
    print("   ✓ Weather data fetched and logged to CSV\n")
    
    # Demo 2: Fetch weather for different locations
    print("2. Fetching weather for different locations...")
    locations = ["London", "Tokyo", "Miami", "Moscow"]
    for location in locations:
        weather_data = logger.fetch_and_log_weather(location)
        print(f"   {location}: {weather_data['current_temperature_celsius']}°C, {weather_data['weather_condition']}")
    print("   ✓ Multiple locations fetched and logged\n")
    
    # Demo 3: Direct use of mock API function
    print("3. Direct use of mock weather API function...")
    mock_data = mock_weather_api("Sydney")
    print(f"   Sydney weather: {mock_data['current_temperature_celsius']}°C, feels like {mock_data['feels_like_celsius']}°C")
    print(f"   Condition: {mock_data['weather_condition']}, Humidity: {mock_data['humidity_percent']}%")
    print("   ✓ Mock API function works independently\n")
    
    # Demo 4: Show logged data
    print("4. Current logged data:")
    stats = logger.get_stats()
    print(f"   Total readings: {stats['count']}")
    print(f"   Temperature range: {stats['min_celsius']:.1f}°C to {stats['max_celsius']:.1f}°C")
    print(f"   Average temperature: {stats['avg_celsius']:.1f}°C")
    
    print("\n✅ Weather Logger with Mock API is working correctly!")
    print("\nThe mock API function 'mock_weather_api()' can be used independently")
    print("or through the WeatherLogger class method 'fetch_and_log_weather()'.")


if __name__ == "__main__":
    main()