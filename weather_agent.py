import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherAgent:
    def __init__(self, location):
        self.location = location
        self.api_key = os.getenv("OPENWEATHER_API_KEY")  # Key loaded from .env
    
    def get_forecast(self):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.location,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if response.status_code != 200:
                return {
                    "error": data.get("message", "API request failed"),
                    "status_code": response.status_code
                }

            temperature = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"].lower()

            rainfall = (
                "high" if "rain" in weather_desc else
                "moderate" if "cloud" in weather_desc else
                "low"
            )

            return {
                "temperature": temperature,
                "rainfall": rainfall,
                "description": weather_desc,
                "humidity": data["main"]["humidity"],  # Added useful field
                "wind_speed": data["wind"]["speed"]   # Added useful field
            }

        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to fetch weather data"
            }