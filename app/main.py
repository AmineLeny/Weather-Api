import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from app.src.weather_cache import redis_client
from contextlib import asynccontextmanager
from app.app_logger import get_logger
from app.src.routes.weather import weather

load_dotenv()

app_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("🚀 Application starting")
    try:
        redis_client.ping()
        app_logger.info("✅ Redis connected")
    except Exception as e:
        app_logger.error(f" ❌ Redis failed : {e}")

    try:
        response = requests.get(
            f"{os.getenv("BASE_URL")}/London/?key={os.getenv('WEATHER_API_KEY')}",
            timeout= 5
        )
        if response.status_code == 200:
            data = response.json()
            
            app_logger.info(
                    f"✅ Weather API test  "
                    f"address : { data['address']} "
                    f"description : {data['description']}"
                    f"Temperature : {data['currentConditions']['temp']}°F"
                
            )
        else:
            app_logger.error(f"❌ Weather API failed: {response.status_code}")

    except requests.RequestException as e:
        app_logger.error(f"❌ Weather API failed: {e}")
    except Exception as e:
        app_logger.error(f"❌ Weather API failed: {e}")

    yield

    app_logger.info("🛑 Application shutting down")



app = FastAPI(
    title="Weather Api",
    description="An Api to get weather conditions based on location",
    lifespan=lifespan,
)

app.include_router(weather, prefix="/api/v1")


@app.get("/")
def healthcheck(): 
    return  {
        "message" : "App is healthy"
    }