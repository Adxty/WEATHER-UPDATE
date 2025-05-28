from dataclasses import dataclass
from typing import List

@dataclass
class WeatherData:
    """
    Represents current weather conditions for a specific location.
    """
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str # OpenWeatherMap icon code
    wind_speed: float
    pressure: int

@dataclass
class DailyForecast:
    """
    Represents aggregated weather forecast for a single day.
    """
    date: str #YYYY-MM-DD
    min_temp: float
    max_temp: float
    avg_temp: float
    description: str
    icon: str # OpenWeatherMap icon code

@dataclass
class ForecastData:
    """
    Represents a collection of daily forecasts for a specific location.
    """
    city: str
    country: str
    daily_forecasts: List[DailyForecast]