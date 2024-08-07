from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from uuid import uuid4
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from dataclasses import dataclass
import os

from data_access.repository import Repository
import utils.google_drive as google_drive
from dependencies.drive_persistence import DrivePersistence
from dependencies.google_cloud_api import GoogleCloudApi
from utils.local_drive import file_exists_on_disk
from data_access.create_connection import create_connection
from settings.config import CONFIG
from utils.parse_stream import MultiPartFormDataParser, parse_http_header_parameters
from dependencies.drive_persistence import DrivePersistence


if not os.path.isdir(CONFIG.FILES_PATH):
    os.mkdir(CONFIG.FILES_PATH)

postgre_repository = Repository(create_connection(CONFIG.POSTGRE_CONNECTION_STR))

postgre_repository.create_schema_if_not_exists()

def get_postgre_repository():
    return postgre_repository

app = FastAPI()


@dataclass
class Metadata:
    uuid: str
    filename: str
    filesize: int
    content_type: str
    extension: str
    was_uploaded_on: datetime


@app.post("/api/upload-file/")
async def upload_file(
        request: Request,
        drive_persistence=Depends(DrivePersistence),
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(get_postgre_repository)
    ):

    # Initialize the multipart form data parser with request headers
    parser = MultiPartFormDataParser(request.headers)
    filesize = 0

    # Generate a unique identifier for the file
    uuid = str(uuid4())

    # Open a file for writing in the specified path using drive persistence
    async with drive_persistence.open(os.path.join(CONFIG.FILES_PATH, uuid)) as out_file:
        # Stream the request data in chunks
        async for chunk in request.stream():
            # Parse each chunk to get the content parts
            content_list = parser.parse_chunk(chunk)
            for content in content_list:
                # Update the file size and write the content to the file
                filesize += len(content)
                await out_file.write(content)

    google_drive.upload_file(os.path.join(CONFIG.FILES_PATH, uuid), uuid, cloud_api)

    # Parse the filename and other metadata from the content headers
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
    
    return 200


def stream_file(path):
    with open(path, mode="rb") as file_like:
        yield from file_like


@app.get("/api/download-file/{uuid}")
async def download_file(
        uuid,
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(get_postgre_repository)
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
    # Return the existing schema if it has already been generated
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
