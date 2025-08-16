from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middlewares import ContextMiddleware, ExceptionHandlerMiddleware
from app.bootstrap import init
from app.config import app_config
from app.database.middleware import DatabaseSessionMiddleware
from app.logger import logger

from .routes import api_router

if app_config.DATABASE_INIT_SEED:
    init(skip_data=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    total_routes = len(app.routes)
    logger.info(f"Starting up 🚀 with {total_routes} routes")

    yield
    # Shutdown

    logger.info("Shutdown complete 🛑")


app = FastAPI(lifespan=lifespan)

# Exceptions are handled by the middleware; so lets clear fastapi's exception handlers, then
# add our own exception handler middleware which will handle basic exceptions and validation errors
app.exception_handlers.clear()
app.add_middleware(ExceptionHandlerMiddleware)

# app.add_middleware(AuthMiddleware, exclude_paths=["/ping"])
app.add_middleware(DatabaseSessionMiddleware)
app.add_middleware(ContextMiddleware)

# include all "root" routers
app.include_router(api_router)
