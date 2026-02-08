from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from upstash_ratelimit import SlidingWindow
from upstash_ratelimit.asyncio import Ratelimit
from upstash_redis.asyncio import Redis

from app.config.log import log
from app.config.env_config import get_settings
from app.utils.constants import messages, origins
from app.config.supabase import supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up LearnX server...")

    try:
        yield
        await redis.close()
    finally:
        log.info("Shutting down the server...")


redis = Redis(
    url=get_settings().UPSTASH_REDIS_REST_URL,
    token=get_settings().UPSTASH_REDIS_REST_TOKEN
)

ratelimit = Ratelimit(
    redis=redis,
    limiter=SlidingWindow(max_requests=10, window=10),
    prefix="@upstash/ratelimit"
)

async def rate_limit_check(request: Request):
    identifier = request.client.host
    result = await ratelimit.limit(identifier)

    if not result.allowed:
        raise HTTPException(status_code=429, detail="Too many requests, Slow down!")
    return result


app = FastAPI(
    title=messages["app_name"],
    description=messages["app_description"],
    version=messages["app_version"],
    lifespan=lifespan,
    dependencies=[Depends(rate_limit_check)]
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_welcome_message():
    return {"message": messages["welcome_message"]}


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Health Check Endpoint",
    description="Endpoint to check the health status of the LearnX server."
)
async def health_check(request: Request):
    health_status = {
        "status": "healthy",
        "dependencies": {
            "database": "unknown",
            "redis": "unknown"
        }
    }

    # 1. Check Redis (Upstash)
    try:
        await redis.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        log.error(f"Redis health check failed: {e}")
        health_status["dependencies"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # 2. Check Supabase
    try:
        # A simple query to check connectivity
        supabase.table("profiles").select("count", count="exact").limit(1).execute()
        health_status["dependencies"]["database"] = "ok"
    except Exception as e:
        health_status["dependencies"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # If any dependency is down, return 503 Service Unavailable
    if health_status["status"] == "unhealthy":
        response = "503_SERVICE_UNAVAILABLE"

    return health_status