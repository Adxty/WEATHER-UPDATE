from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from rich.columns import Columns
from weather_data import WeatherData, ForecastData, DailyForecast

class WeatherDisplay:
    """
    Handles the visual presentation of weather data in the terminal using Rich.
    Provides methods to display current weather and forecast information
    with rich formatting, colors, and a simple text-based visualization.
    """
    # Mapping OpenWeatherMap icon codes to Rich-compatible emojis
    # A more comprehensive mapping could be added.
    WEATHER_ICONS = {
        "01d": "☀️", "01n": "🌙",
        "02d": "🌤️", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️",
        "unknown": "❓" # Fallback for unknown icons
    }

    def __init__(self, console: Console):
        """
        Initializes the WeatherDisplay with a Rich Console instance.
        Args:
            console (Console): The Rich Console object to print to.
        """
        self.console = console

    def _get_weather_emoji(self, icon_code: str) -> str:
        """
        Returns an emoji corresponding to the OpenWeatherMap icon code.
        Args:
            icon_code (str): The icon code from OpenWeatherMap.
        Returns:
            str: An emoji character.
        """
        return self.WEATHER_ICONS.get(icon_code, self.WEATHER_ICONS["unknown"])

    def display_current_weather(self, data: WeatherData):
        """
        Displays the current weather data in a formatted table.
        Args:
            data (WeatherData): The current weather data object.
        """
        table = Table(
            title=f"[bold blue]Current Weather in {data.city}, {data.country}[/bold blue]",
            title_style="bold underline",
            header_style="bold green",
            border_style="purple",
            box=ROUNDED
        )

        table.add_column("Property", style="cyan", justify="left")
        table.add_column("Value", style="yellow", justify="right")

        table.add_row("Temperature", f"[bold red]{data.temperature:.1f}°C[/bold red] {self._get_weather_emoji(data.icon)}")
        table.add_row("Feels Like", f"{data.feels_like:.1f}°C")
        table.add_row("Description", f"[italic]{data.description}[/italic]")
        table.add_row("Humidity", f"{data.humidity}%")
        table.add_row("Wind Speed", f"{data.wind_speed:.1f} m/s")
        table.add_row("Pressure", f"{data.pressure} hPa")

        self.console.print(Panel(table, title="[bold magenta]Current Conditions[/bold magenta]", border_style="green", box=ROUNDED))
        self.console.print("\n") # Add a newline for spacing

    def display_forecast(self, data: ForecastData):
        """
        Displays the 5-day weather forecast, including a text-based temperature trend visualization.
        Args:
            data (ForecastData): The forecast data object.
        """
        self.console.print(Panel(
            Text(f"📅 5-Day Forecast for {data.city}, {data.country} 📅", justify="center", style="bold blue"),
            title="[bold blue]Forecast Overview[/bold blue]",
            title_align="center",
            border_style="magenta",
            box=ROUNDED
        ))

        forecast_panels = []
        min_temp_all = min(d.min_temp for d in data.daily_forecasts)
        max_temp_all = max(d.max_temp for d in data.daily_forecasts)

        for day in data.daily_forecasts:
            # Create a small panel for each day's forecast
            day_panel_content = Text()
            day_panel_content.append(f"{day.date}\n", style="bold yellow")
            day_panel_content.append(f"{self._get_weather_emoji(day.icon)} {day.description}\n")
            day_panel_content.append(f"Min: [blue]{day.min_temp:.1f}°C[/blue]\n")
            day_panel_content.append(f"Max: [red]{day.max_temp:.1f}°C[/red]\n")
            day_panel_content.append(f"Avg: [green]{day.avg_temp:.1f}°C[/green]")

            forecast_panels.append(Panel(
                day_panel_content,
                title=f"[bold cyan]{day.date.split('-')[2]}[/bold cyan]", # Just the day number
                border_style="purple",
                box=ROUNDED,
                width=20 # Fixed width for consistent layout
            ))

        # Use Columns to arrange daily forecast panels horizontally
        self.console.print(Columns(forecast_panels, expand=True, align="center"))
        self.console.print("\n")

        # --- Text-based Temperature Trend Visualization ---
        self.console.print(Panel(
            Text("📊 Daily Temperature Trend 📊", justify="center", style="bold cyan"),
            title="[bold cyan]Visualization[/bold cyan]",
            title_align="center",
            border_style="yellow",
            box=ROUNDED
        ))

        # Normalize temperatures for ASCII art scaling
        # We'll create a simple bar chart or sparkline
        chart_height = 8 # Number of rows for the chart
        chart_width = 50 # Max width for the temperature bar

        # Ensure there's a range to avoid division by zero if all temps are same
        temp_range = max_temp_all - min_temp_all
        if temp_range == 0:
            temp_range = 1 # Prevent division by zero

        chart_lines = [" " * chart_width for _ in range(chart_height)]

        for i, day in enumerate(data.daily_forecasts):
            # Scale temperature to chart height
            # Using average temperature for the trend line
            scaled_temp = int(((day.avg_temp - min_temp_all) / temp_range) * (chart_height - 1))
            scaled_temp = max(0, min(scaled_temp, chart_height - 1)) # Clamp values

            # Place a marker (e.g., '●') at the scaled temperature level
            # We'll use a simple character for the trend
            column_pos = int((i / (len(data.daily_forecasts) - 1)) * (chart_width - 1)) if len(data.daily_forecasts) > 1 else 0
            column_pos = max(0, min(column_pos, chart_width - 1))

            # Draw the marker
            # We use a mutable list of characters for each line to update it
            line_chars = list(chart_lines[chart_height - 1 - scaled_temp])
            line_chars[column_pos] = '●'
            chart_lines[chart_height - 1 - scaled_temp] = "".join(line_chars)

            # Add temperature labels below the chart
            # This part is tricky to align perfectly in a simple text chart,
            # so we'll just put them below.
            self.console.print(f"[dim]{day.date.split('-')[2]}[/dim]: [bold green]{day.avg_temp:.1f}°C[/bold green]", justify="center")

        # Print the ASCII chart lines
        for line in chart_lines:
            self.console.print(f"[dim]|{line}|[/dim]", justify="center")

        # Add x-axis labels (dates)
        date_labels = [day.date.split('-')[2] for day in data.daily_forecasts]
        self.console.print(Text(" ".join(date_labels).center(chart_width + 2), style="dim"), justify="center")
        self.console.print(Text("Days".center(chart_width + 2), style="dim"), justify="center")

        self.console.print("\n") # Add a newline for spacing