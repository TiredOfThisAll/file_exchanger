import os
import importlib
from fastapi import APIRouter

api_router = APIRouter()


router_dir = os.path.join(os.path.dirname(__file__), "api")
for filename in os.listdir(router_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"endpoints.api.{filename[:-3]}"
        module = importlib.import_module(module_name)
        if hasattr(module, "router"):
            api_router.include_router(module.router)
