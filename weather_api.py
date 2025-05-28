import httpx # Use httpx for async requests
import os
from typing import Optional, Dict, Any, List
from weather_data import WeatherData, ForecastData, DailyForecast

class WeatherAPI:
    """
    Handles interactions with the OpenWeatherMap API.
    Fetches current weather and 5-day forecast data.
    """
    BASE_URL = "https://api.openweathermap.org/data/2.5/"

    def __init__(self, api_key: str):
        """
        Initializes the WeatherAPI client with the API key.
        Args:
            api_key (str): Your OpenWeatherMap API key.
        """
        self.api_key = api_key
        # Initialize an asynchronous HTTP client
        self.client = httpx.AsyncClient()

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Internal helper to make an asynchronous HTTP GET request to the API.
        Args:
            endpoint (str): The API endpoint (e.g., "weather", "forecast").
            params (Dict[str, Any]): Dictionary of query parameters.
        Returns:
            Optional[Dict[str, Any]]: JSON response data if successful, None otherwise.
        """
        full_url = f"{self.BASE_URL}{endpoint}"
        # Add common parameters
        params.update({"appid": self.api_key, "units": "metric"}) # Use metric units by default

        try:
            response = await self.client.get(full_url, params=params, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except httpx.RequestError as e:
            print(f"Network error during request to {e.request.url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {e.request.url}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    async def get_current_weather(self, city_name: str) -> Optional[WeatherData]:
        """
        Fetches current weather data for a given city.
        Args:
            city_name (str): The name of the city.
        Returns:
            Optional[WeatherData]: A WeatherData object if successful, None otherwise.
        """
        params = {"q": city_name}
        data = await self._make_request("weather", params)

        if data:
            try:
                # Extract relevant information and create a WeatherData object
                return WeatherData(
                    city=data['name'],
                    country=data['sys']['country'],
                    temperature=data['main']['temp'],
                    feels_like=data['main']['feels_like'],
                    humidity=data['main']['humidity'],
                    description=data['weather'][0]['description'].capitalize(),
                    icon=data['weather'][0]['icon'],
                    wind_speed=data['wind']['speed'],
                    pressure=data['main']['pressure']
                )
            except KeyError as e:
                print(f"Error parsing current weather data: Missing key {e} in response.")
                return None
        return None

    async def get_five_day_forecast(self, city_name: str) -> Optional[ForecastData]:
        """
        Fetches 5-day weather forecast data for a given city (3-hour step).
        Args:
            city_name (str): The name of the city.
        Returns:
            Optional[ForecastData]: A ForecastData object if successful, None otherwise.
        """
        params = {"q": city_name}
        data = await self._make_request("forecast", params)

        if data:
            try:
                daily_forecasts: List[DailyForecast] = []
                # Group forecast data by day to get daily min/max and average
                # This is a simplification, as OpenWeatherMap provides 3-hour steps.
                # We'll aggregate for a cleaner daily view.
                forecast_by_day: Dict[str, List[Dict[str, Any]]] = {}

                for item in data['list']:
                    date = item['dt_txt'].split(' ')[0] #YYYY-MM-DD
                    if date not in forecast_by_day:
                        forecast_by_day[date] = []
                    forecast_by_day[date].append(item)

                for date_str, readings in forecast_by_day.items():
                    temps = [r['main']['temp'] for r in readings]
                    descriptions = [r['weather'][0]['description'] for r in readings]
                    icons = [r['weather'][0]['icon'] for r in readings]

                    # Find the most common description for the day
                    from collections import Counter
                    most_common_description = Counter(descriptions).most_common(1)[0][0].capitalize()
                    most_common_icon = Counter(icons).most_common(1)[0][0]

                    daily_forecasts.append(DailyForecast(
                        date=date_str,
                        min_temp=min(temps),
                        max_temp=max(temps),
                        avg_temp=sum(temps) / len(temps),
                        description=most_common_description,
                        icon=most_common_icon
                    ))

                # Sort forecasts by date
                daily_forecasts.sort(key=lambda x: x.date)

                return ForecastData(
                    city=data['city']['name'],
                    country=data['city']['country'],
                    daily_forecasts=daily_forecasts
                )
            except KeyError as e:
                print(f"Error parsing forecast data: Missing key {e} in response.")
                return None
            except Exception as e:
                print(f"An unexpected error occurred during forecast parsing: {e}")
                return None
        return None