from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from uuid import uuid4
from fastapi.openapi.utils import get_openapi
from datetime import datetime
import os

import utils.google_drive as google_drive
from dependencies.drive_persistence import DrivePersistence
from dependencies.google_cloud_api import GoogleCloudApi
from dependencies.postgres_repository import PostgresRepository
from utils.local_drive import file_exists_on_disk
from settings.config import CONFIG
from utils.parse_stream import MultiPartFormDataParser, parse_http_header_parameters
from dependencies.drive_persistence import DrivePersistence
from data_classes.metadata import Metadata
from middlewares.limit_file_size import FileSizeLimitMiddleware


if not os.path.isdir(CONFIG.FILES_PATH):
    os.mkdir(CONFIG.FILES_PATH)

PostgresRepository.create_db_if_not_exists()
PostgresRepository.create_schema_if_not_exists()

app = FastAPI()
app.add_middleware(FileSizeLimitMiddleware, max_file_size=CONFIG.MAX_FILE_SIZE)


@app.post("/api/upload-file/")
async def upload_file(
        request: Request,
        drive_persistence=Depends(DrivePersistence),
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(PostgresRepository)
    ):

    parser = MultiPartFormDataParser(request.headers)
    filesize = 0

    uuid = str(uuid4())

    # Save file from stream
    async with drive_persistence.open(os.path.join(CONFIG.FILES_PATH, uuid)) as out_file:
        async for chunk in request.stream():
            content_list = parser.parse_chunk(chunk)
            for content in content_list:
                filesize += len(content)
                await out_file.write(content)

    google_drive.upload_file(os.path.join(CONFIG.FILES_PATH, uuid), uuid, cloud_api)

    filename = parse_http_header_parameters(
        parser.content_headers["Content-Disposition"]
    )["filename"]
    filename, ext = os.path.splitext(filename)
    content_type = parser.content_headers["Content-Type"]
    
    was_uploaded_on = datetime.now()

    metadata = Metadata(
        uuid,
        filename,
        filesize,
        content_type,
        ext,
        was_uploaded_on
    )

    repository.insert_new_metadata(metadata)
    
    return JSONResponse({"uuid": uuid}, 200)


def stream_file(path):
    with open(path, mode="rb") as file_like:
        yield from file_like


@app.get("/api/download-file/{uuid}")
async def download_file(
        uuid,
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(PostgresRepository)
    ):

    metadata = repository.get_metadata_by_uuid(uuid)

    if not file_exists_on_disk(CONFIG.FILES_PATH, uuid):
        # If the file does not exist, attempt to download it from the cloud
        error = cloud_api.download_file(CONFIG.FILES_PATH, uuid)
        if error is not None:
            return JSONResponse({"error": uuid})

    filename = metadata.name + metadata.extension

    return StreamingResponse(
        stream_file(os.path.join(CONFIG.FILES_PATH, uuid)),
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        media_type=metadata.format
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Generate a new OpenAPI schema with a custom title, version, and routes
    openapi_schema = get_openapi(title="Custom title", version="1.0.0", routes=app.routes)
    # Modify the requestBody for the /api/upload-file/ endpoint to handle multipart/form-data
    openapi_schema['paths']['/api/upload-file/']['post']['requestBody'] = {
        'content': {'multipart/form-data': {'schema': {'$ref': '#/components/schemas/Body_hey_file_post'}}},
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
