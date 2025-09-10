import argparse
import requests
from .utils import get_weather, display_weather


def get_city_from_ip():
    """
    Detect city using the user's IP address.
    Returns city name or None if detection fails.
    """
    try:
        response = requests.get("http://ip-api.com/json/")
        response.raise_for_status()
        data = response.json()
        return data.get("city")
    except requests.RequestException:
        return None


def run_cli(city=None, units="C"):
    """
    Run the CLI logic. Can be called directly from tests.
    Args:
        city (str): Name of the city
        units (str): "C" (default), "F", or "K"
    """
    if not city:
        print("City not provided. Detecting your location...")
        city = get_city_from_ip()
        if city:
            print(f"Detected location: {city}")
        else:
            print("Could not detect location. Please provide a city using --city.")
            return

    # Map CLI units to OpenWeather API units
    unit_map = {"C": "metric", "F": "imperial", "K": "standard"}
    api_units = unit_map.get(units, "metric")  # default to metric (Celsius)

    data = get_weather(city, api_units)
    if data:
        display_weather(data, units)
    else:
        print("Could not fetch weather data. Check your city name or API key.")


def main():
    parser = argparse.ArgumentParser(description="Fetch live weather data for a given city using OpenWeather API.")
    parser.add_argument("--city", type=str, help="Name of the city to fetch weather for")
    # Units argument removed for simplicity; defaults to "C"
    args = parser.parse_args()
    run_cli(city=args.city)  # units defaults to "C"


if __name__ == "__main__":
    main()
