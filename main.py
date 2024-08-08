import os
import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


from app.dependencies.postgres_repository import PostgresRepository
from app.middlewares.limit_file_size import FileSizeLimitMiddleware
from app.endpoints.api_router import api_router
from settings.config import CONFIG


if not os.path.isdir(CONFIG.FILES_PATH):
    os.mkdir(CONFIG.FILES_PATH)

if not os.path.isdir(CONFIG.LOGS_PATH):
    os.mkdir(CONFIG.LOGS_PATH)

logging.basicConfig(
            filename=os.path.join(CONFIG.LOGS_PATH, CONFIG.LOGS_FILE_NAME),
            encoding='utf-8',
            level=logging.DEBUG
        )

PostgresRepository.create_db_if_not_exists()
PostgresRepository.create_schema_if_not_exists()

app = FastAPI()
app.add_middleware(FileSizeLimitMiddleware, max_file_size=CONFIG.MAX_FILE_SIZE)
app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # Generate a new OpenAPI schema with a custom title, version, and routes
    openapi_schema = get_openapi(title="Custom title", version="1.0.0", routes=app.routes)
    # Modify the requestBody for the /api/upload-file/ endpoint to handle multipart/form-data
    openapi_schema['paths']['/api/upload-file/']['post']['requestBody'] = {
        'content': {'multipart/form-data': {
            'schema': {'$ref': '#/components/schemas/Body_hey_file_post'
        }}},
        'required': True
    }

    if 'components' not in openapi_schema:
        openapi_schema['components'] = {}

    if 'schemas' not in openapi_schema['components']:
        openapi_schema['components']['schemas'] = {}

    # Define the schema for the request body of the /api/upload-file/ endpoint
    openapi_schema['components']['schemas']['Body_hey_file_post'] = {
        'properties': {'file': {'format': 'binary', 'title': 'File', 'type': 'string'}},
        'required': ['file'], 'title': 'Body_hey_file_post', 'type': 'object'
    }

    # Cache the generated schema in the application to avoid regenerating it
    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi
