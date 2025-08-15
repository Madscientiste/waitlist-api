from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.api.middlewares import ContextMiddleware
from app.context.app import get_app_context
from app.database.connection import db
from app.database.middleware import DatabaseSessionMiddleware
from app.database.model import BaseModel
from app.exceptions.base import BaseAppException
from app.exceptions.basic import InternalError
from app.exceptions.handlers import handle_validation_error
from app.logger import logger

from .routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Here we will initialize the database schema since we will not add a migration system

    total_routes = len(app.routes)
    logger.info(f"Starting up 🚀 with {total_routes} routes")

    yield

    # Shutdown

    logger.info("Shutdown complete 🛑")


app = FastAPI(lifespan=lifespan)


# Global fallback for uncaught exceptions
@app.middleware("http")
async def exc_handler(request: Request, call_next):
    last_exc = None

    try:
        return await call_next(request)
    except BaseAppException as exc:
        # logger.exception(exc)
        last_exc = exc
        return exc.to_json_response()
    except Exception as exc:
        # logger.exception(exc)
        last_exc = exc
        return InternalError(message="Internal Server Error").to_json_response()
    finally:
        ctx = get_app_context()

        # Here we could send the request to a metrics/monitoring system, like sentry or datadog
        # In production is really recommended as this will help track things more easily
        logger.error(f"Sent to sentry; request_id: {ctx.http.get('request_id')};")
        logger.error(f"Last exception: {last_exc}")
        logger.error(f"Last exception type: {type(last_exc)}")


# app.add_middleware(AuthMiddleware, exclude_paths=["/ping"])
app.add_middleware(DatabaseSessionMiddleware)
app.add_middleware(ContextMiddleware)

# include all "root" routers
app.include_router(api_router)

# Exception handling goes here
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(PydanticValidationError, handle_validation_error)
