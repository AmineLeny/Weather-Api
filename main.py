import requests
import os
from dotenv import load_dotenv


load_dotenv()


base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

response = requests.get(
    f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/?key={os.getenv('WEATHER_API_KEY')}"
)

data = response.json()

print(
    {
        "address": data["address"],
        "description": data["description"],
        "Temperature": data["currentConditions"]["temp"],
    }
)
