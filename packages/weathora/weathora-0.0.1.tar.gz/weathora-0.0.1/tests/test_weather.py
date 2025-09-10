import os
import pytest
from weathora.utils import get_weather, display_weather, get_city_from_ip
from weathora.cli import run_cli

# Skip tests if API_KEY not set
API_KEY = os.getenv("OPENWEATHER_API_KEY")
pytest.skip("OPENWEATHER_API_KEY not set", allow_module_level=True) if not API_KEY else None


def test_get_city_from_ip():
    """Test that IP-based city detection returns a non-empty string or None."""
    city = get_city_from_ip()
    # It can return None if IP detection fails
    assert city is None or isinstance(city, str)
    if city:
        assert len(city) > 0


def test_get_weather_with_city():
    """Test fetching weather for a valid city."""
    city = "London"
    data = get_weather(city=city, units="metric")
    assert data is not None
    assert data["name"].lower() == city.lower()
    assert "main" in data
    assert "temp" in data["main"]


def test_get_weather_with_ip_detection():
    """Test fetching weather without providing a city (uses IP)."""
    data = get_weather(city=None, units="metric")
    # Might fail if IP detection fails
    if data is not None:
        assert "main" in data
        assert "temp" in data["main"]
        assert "name" in data


def test_display_weather_output(capsys):
    """Test that display_weather prints table without errors."""
    city = "New York"
    data = get_weather(city=city, units="metric")
    if data:
        display_weather(data, units="C")
        captured = capsys.readouterr()
        assert city.lower() in captured.out.lower()


def test_run_cli_with_city(capsys):
    """Test the CLI function with a city argument."""
    run_cli(city="Paris", units="C")
    captured = capsys.readouterr()
    assert "Paris" in captured.out


def test_run_cli_without_city(capsys):
    """Test the CLI function without providing city (IP detection)."""
    run_cli(city=None, units="C")
    captured = capsys.readouterr()
    # Either IP-detected city or error message
    assert "Could not detect location" in captured.out or "Weather in" in captured.out
