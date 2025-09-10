import os
import requests
from rich import print
from rich.table import Table

API_KEY = os.getenv("OPENWEATHER_API_KEY")  # make sure it's set
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Emojis for weather conditions
WEATHER_EMOJIS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "💧",
    "Thunderstorm": "🌩️",
    "Snow": "❄️",
    "Mist": "🌫️",
}


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


def get_weather(city: str = None, units="metric"):
    """
    Fetch weather data from OpenWeather API.

    Args:
        city (str): Name of the city. If None, tries IP-based detection.
        units (str): "metric" (°C), "imperial" (°F), "standard" (K)
                     Defaults to "metric" (Celsius)

    Returns:
        dict or None: API response or None on error
    """
    if city is None:
        city = get_city_from_ip()
        if city is None:
            print("[red]Could not detect location via IP. Provide a city.[/red]")
            return None

    params = {"q": city, "appid": API_KEY, "units": units}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[red]Error fetching weather:[/red] {e}")
        return None


def display_weather(data: dict, units="C"):
    """
    Display weather information in a formatted table using Rich.

    Args:
        data (dict): API response from OpenWeather
        units (str): "C" (°C), "F" (°F), "K" (Kelvin)
                     Defaults to "C"
    """
    weather_main = data["weather"][0]["main"]
    emoji = WEATHER_EMOJIS.get(weather_main, "")

    # Determine unit symbol
    unit_symbol = "°C" if units == "C" else "°F" if units == "F" else "K"

    table = Table(title=f"Weather in {data['name']}, {data['sys']['country']} {emoji}")
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Temperature", f"{data['main']['temp']}{unit_symbol}")
    table.add_row("Feels Like", f"{data['main']['feels_like']}{unit_symbol}")
    table.add_row("Humidity", f"{data['main']['humidity']}%")
    table.add_row("Weather", f"{data['weather'][0]['description'].title()} {emoji}")
    table.add_row("Wind Speed", f"{data['wind']['speed']} m/s")
    table.add_row("Pressure", f"{data['main']['pressure']} hPa")
    table.add_row("Visibility", f"{data.get('visibility', 'N/A')} m")
    table.add_row("Cloudiness", f"{data['clouds']['all']}%")

    print(table)
