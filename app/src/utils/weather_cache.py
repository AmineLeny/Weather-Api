import redis 
from datetime import datetime
from fastapi import HTTPException, Request
from app.src.utils.app_logger import get_logger

app_logger = get_logger(__name__)

redis_client = redis.Redis(
    host='localhost', 
    port=6379,
    decode_responses=True
    )



def check_rate_limit(
        request: Request,
        max_requests : int =10,
        window_seconds : int = 60
) -> None :
    
    client_ip = request.client.host
    client_minute = datetime.now().strftime("%Y%m%d%H%M")

    key = f"rate_limit:{client_ip}:{client_minute}"

    try : 
        current_rate = redis_client.incr(key)
        app_logger.debug(f"Rate limit : {client_ip} -> {(current_rate/max_requests)*100:.1f} %")

        if current_rate == 1 :
            redis_client.expire(key, window_seconds)

        if current_rate > max_requests : 
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {max_requests} per {window_seconds} seconds"
            )
        
    except HTTPException : 
        raise
    
    except Exception as e  :
        app_logger.error(f"Unexpected error happened : {e}")
