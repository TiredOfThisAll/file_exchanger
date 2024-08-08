import os
from fastapi import Request, Depends, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from app.dependencies.google_cloud_api import GoogleCloudApi
from app.dependencies.postgres_repository import PostgresRepository
from app.dependencies.main_logger import MainLogger

from app.utils.local_drive import file_exists_on_disk
from app.utils import google_drive
from settings.config import CONFIG

router = APIRouter()


def stream_file(path):
    with open(path, mode="rb") as file_like:
        yield from file_like


@router.get("/api/download-file/{uuid}")
async def download_file(
        request: Request,
        uuid,
        cloud_api=Depends(GoogleCloudApi),
        repository=Depends(PostgresRepository),
        logger=Depends(MainLogger)
    ):

    logger.info(f"{request.url.hostname}:{request.url.port} - {request.method} {request.url.path}")

    metadata = repository.get_metadata_by_uuid(uuid)

    if not file_exists_on_disk(CONFIG.FILES_PATH, uuid):
        # If the file does not exist, attempt to download it from the cloud
        error = google_drive.download_file(CONFIG.FILES_PATH, uuid, cloud_api, logger)
        if error is not None:
            if error.startswith("File with uuid"):
                return JSONResponse({"error": error}, 404)
            return JSONResponse({"error": error}, 502)

    filename = metadata.name + metadata.extension

    return StreamingResponse(
        stream_file(os.path.join(CONFIG.FILES_PATH, uuid)),
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        media_type=metadata.format
    )
