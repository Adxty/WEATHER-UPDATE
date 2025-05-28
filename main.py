import os
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from weather_api import WeatherAPI
from weather_display import WeatherDisplay
from weather_data import WeatherData, ForecastData
import asyncio

# Initialize Rich Console for beautiful terminal output
console = Console()

async def main():
    """
    Main asynchronous function to run the weather application.
    It handles user input, fetches data, and displays it.
    """
    console.print(Panel(
        Text("✨ Welcome to the PyWeather Forecast! ✨", justify="center", style="bold green"),
        title="[bold blue]PyWeather[/bold blue]",
        title_align="center",
        border_style="cyan",
        box=ROUNDED
    ))

    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        console.print(Panel(
            Text("🚨 [bold red]API Key Missing![/bold red] Please set the 'OPENWEATHER_API_KEY' environment variable.\n"
                 "You can get a free API key from OpenWeatherMap (openweathermap.org/api).",
                 justify="center", style="yellow"),
            title="[bold red]Configuration Error[/bold red]",
            border_style="red",
            box=ROUNDED
        ))
        sys.exit(1) # Exit if API key is not found

    weather_api = WeatherAPI(api_key)
    weather_display = WeatherDisplay(console)

    while True:
        city = Prompt.ask("[bold magenta]Enter city name[/bold magenta] (e.g., London, Tokyo, New York) or 'exit' to quit")

        if city.lower() == 'exit':
            console.print(Panel(
                Text("👋 Thank you for using PyWeather! Goodbye! 👋", justify="center", style="bold green"),
                title="[bold blue]Exiting[/bold blue]",
                title_align="center",
                border_style="cyan",
                box=ROUNDED
            ))
            break

        console.print(f"[bold yellow]Fetching weather for {city}...[/bold yellow]")

        # Fetch current weather
        current_weather_data = await weather_api.get_current_weather(city)
        if current_weather_data:
            weather_display.display_current_weather(current_weather_data)
        else:
            console.print(f"[bold red]Could not retrieve current weather for {city}. Please check the city name.[/bold red]")

        # Fetch forecast
        forecast_data = await weather_api.get_five_day_forecast(city)
        if forecast_data:
            weather_display.display_forecast(forecast_data)
        else:
            console.print(f"[bold red]Could not retrieve forecast for {city}.[/bold red]")

        console.print("\n" + "="*80 + "\n") # Separator for next query

if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())