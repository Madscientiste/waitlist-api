from fastapi import APIRouter
from pydantic import BaseModel

from app import logger
from app.config import app_config
from app.context.app import get_app_context
from app.models.health import Health

router = APIRouter(tags=["health"])


@router.get("/ping")
async def ping():
    health = Health.create_health()
    ctx = get_app_context()
    http_ctx = ctx.http

    return {
        "message": "pong",
        "health": health,
        "path": http_ctx.get("path"),
        "method": http_ctx.get("method"),
        "request_id": http_ctx.get("request_id"),
    }


if app_config.ENVIRONMENT in ["local", "testing"]:
    logger.info(f"Added testing routes; '/error' and '/error/validation'")

    @router.get("/error")
    async def uncaught_error():
        raise Exception("test")

    @router.get("/error/validation")
    async def validation_error():
        class ExampleModel(BaseModel):
            name: str
            age: int

        ExampleModel(name="John", age="twenty")
