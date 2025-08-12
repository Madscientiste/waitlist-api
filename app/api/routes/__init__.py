import os
from importlib import import_module

from fastapi import APIRouter

from app.config import APP_ROUTES_MODULES

api_router = APIRouter(prefix="/api/v1")

# Here we either includes manually or just let the
# auto-importing thing do its things
#
## routes to be imported if using manual import
# from .users import router as users_router
# from .groups import router as groups_router
# api_router.include_router(...)

# import all routes from the routes folder
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        router = import_module(f"{APP_ROUTES_MODULES}.{file[:-3]}")
        api_router.include_router(router.router)
