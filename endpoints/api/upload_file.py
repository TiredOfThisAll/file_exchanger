from uuid import uuid4
from datetime import datetime
import os
from fastapi import Request, Depends, APIRouter
from fastapi.responses import JSONResponse

from dependencies.drive_persistence import DrivePersistence
from dependencies.google_cloud_api import GoogleCloudApi
from dependencies.postgres_repository import PostgresRepository
from dependencies.main_logger import MainLogger

from utils import google_drive
from utils.parse_stream import MultiPartFormDataParser, parse_http_header_parameters
from settings.config import CONFIG
from data_classes.metadata import Metadata


router = APIRouter()


@router.post("/api/upload-file/")
async def upload_file(
        request: Request,
        drive_persistence=Depends(DrivePersistence),
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(PostgresRepository),
        logger=Depends(MainLogger)
    ):

    request_url = f"{request.url.hostname}:{request.url.port}"
    logger.info(f"{datetime.now()}|{request_url} - {request.method} {request.url.path}")

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

    filename = parse_http_header_parameters(
        parser.content_headers["Content-Disposition"]
    )["filename"]
    filename, ext = os.path.splitext(filename)
    content_type = parser.content_headers["Content-Type"]

    was_uploaded_on = datetime.now()

    logger.info(f"{datetime.now()}|File {filename + ext} uploaded on drive")

    error = google_drive.upload_file(
        os.path.join(CONFIG.FILES_PATH, uuid),
        uuid,
        cloud_api,
        logger
    )

    if error:
        return JSONResponse({"error": error}, 502)

    logger.info(f"{datetime.now()}|File {filename + ext} uploaded on cloud")

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
