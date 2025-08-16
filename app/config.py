"""
Configuration module for application settings.
"""

import logging
from typing import Any, Literal

from pydantic import computed_field
from pydantic_core import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.table import Table
from sqlalchemy.engine import URL

from app.logger import logger


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # == Project ==
    ENVIRONMENT: Literal["prod", "dev", "testing", "local"] = "local"

    # == Database ==
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_DB: str

    DATABASE_FORCE_SQLITE: bool = False
    DATABASE_DEBUG: bool = False
    DATABASE_POOL_SIZE: int = 60

    @computed_field
    @property
    def ENGINE_ARGUMENTS(self) -> dict[str, Any]:
        ARGS = {
            "url": URL.create(
                "postgresql+psycopg2",
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                database=self.DATABASE_DB,
            ),
            "pool_pre_ping": True,
            "pool_size": 60,
            # Debug
            "echo": False,
            "echo_pool": False,
            #
            "connect_args": {
                "connect_timeout": 10,
                "options": "-c timezone=Europe/Paris",
            },
        }

        # Makes testing easier; but in the future using the same database as prod is recommended
        if self.ENVIRONMENT in ["ci", "local", "testing"] or self.DATABASE_FORCE_SQLITE:
            ARGS["url"] = f"sqlite:///{self.DATABASE_DB}.db"
            del ARGS["connect_args"]

        return ARGS

    @computed_field
    @property
    def SESSION_ARGUMENTS(self) -> dict[str, Any]:
        return {
            "autocommit": False,
            "autoflush": False,
        }


try:
    print()
    logger.info("Loading configuration...")
    app_config = AppConfig()

    # set the logger level depending on the environment
    if app_config.ENVIRONMENT in ["local", "testing"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug(f"Logger level set to {logger.level}")

except ValidationError as exc:
    logger.error("Missing environment variables, please check your .env file")
    console = Console()

    table = Table()
    table.add_column("Field", style="cyan")
    table.add_column("Message", style="white")

    for error in exc.errors():
        table.add_row(
            error["loc"][0] if error["loc"] else "unknown",
            error["msg"],
        )

    console.log(table)
    exit(1)
