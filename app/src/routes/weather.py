from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv
from app.src.weather_cache import redis_client
from app.app_logger import get_logger
import json


app_logger = get_logger(__name__)
load_dotenv()

weather = APIRouter(prefix="/weather", tags=["WeatherAPI"])
params = {"key": os.getenv("WEATHER_API_KEY")}


@weather.get("/{location}")
async def get_weather_info(location: str) -> dict:
    """
    Get weather information for a location
    data is cached for 12 hours

    """
    try:
        cached_data = redis_client.get(f"weather:{location}")
        if cached_data:
            app_logger.info(f"Cache hit for {location}")
            return json.loads(cached_data)

    except Exception as e:
        app_logger.exception(f"Caching read failed : {e}")

    app_logger.info(f"🌐 Cache MISS - fetching from API for {location}")

    try:
        response = requests.get(f"{os.getenv('BASE_URL')}/{location}/", params=params, timeout=5)
        if (200 <= response.status_code < 300):
            app_logger.info("Client request is successful")
            data = response.json()

            client_response = {
                "address": data["address"],
                "description": data["description"],
                "Temperature": f"{data["currentConditions"]["temp"]} F",
            }
            redis_client.setex(
                f"weather:{location}", 43200, json.dumps(client_response)
            )
            app_logger.info(f"💾 Cached weather for {location} (12h TTL)")
            return client_response
        else:
            app_logger.info(f"Api error for {location}: HTTP :{response.status_code}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Weather service returned status {response.status_code}",
            )
    except HTTPException : 
        raise
    except requests.Timeout as e : 
        app_logger.exception(f"Request Timeout for weather in : {location} : {e}")
        raise HTTPException(
            status_code=504,
            detail="Weather service unavailable"
        )
    
    except requests.RequestException as e:
        app_logger.error(f"Client request failed : {e}")
        raise HTTPException(status_code=503, detail="Weather service unavailable")
    except KeyError as e : 
        app_logger.exception(f"Missing key in API response: {e}")
        raise HTTPException(
            status_code=502,
            detail="Invalid response from weather service"
        )
    except Exception as e:
        app_logger.exception(f"Unexpected error: {e} ")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error"
        )
