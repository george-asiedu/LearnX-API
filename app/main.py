from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from upstash_ratelimit import SlidingWindow
from upstash_ratelimit.asyncio import Ratelimit
from upstash_redis.asyncio import Redis

from app.config.log import log
from app.config.env_config import get_settings
from app.utils.constants import messages, origins
from app.config.supabase import supabase, engine
from sqlmodel import text, Session
from app.utils.exceptions import APIException
from app.utils.error_handler import global_exception_handler


is_production = get_settings().ENVIRONMENT != 'development'

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up LearnX server...")

    # 1. Check Database Connection
    try:
        # We use the engine directly, not a session, for a connectivity check
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        log.info("✅ Database (PostgreSQL) is connected.")
    except Exception as e:
        log.error(f"❌ Database connection failed: {e}")
        raise e

    # 2. Check Supabase API
    try:
        # Simple check to Supabase if we can form a query, even if empty
        supabase.table("profiles").select("count", count="exact").limit(1).execute()
        log.info("✅ Supabase is reachable.")
    except Exception as e:
        log.error(f"❌ Supabase check failed: {e}")

    yield

    log.info("Shutting down the server...")
    await redis.close()
    engine.dispose()


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
        raise APIException(status_code=429, message="Too many requests, Slow down!")
    return result


app = FastAPI(
    title=messages["app_name"],
    description=messages["app_description"],
    version=messages["app_version"],
    lifespan=lifespan,
    dependencies=[Depends(rate_limit_check)],
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    #Create a session for this specific request
    with Session(engine) as session:
        #Attach it to the request state
        request.state.db = session
        request.state.supabase = supabase

        #Proceed to the next middleware or actual request handler
        response = await call_next(request)

    #Session automatically closes here when "with" block ends
    return response

@app.get("/", tags=["Welcome"])
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

app.add_exception_handler(APIException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)