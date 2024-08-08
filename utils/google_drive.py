from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpError
import asyncio
from datetime import datetime

from settings.config import CONFIG


service = build(
    'drive',
    'v3',
    credentials=service_account.Credentials.from_service_account_file(
        filename=CONFIG.GOOGLE_API_KEY_PATH,
        scopes=['https://www.googleapis.com/auth/drive']
))


def upload_file(path, file_uuid, google_cloud_api, logger):
    try:
        asyncio.get_event_loop().run_in_executor(
            None,
            google_cloud_api.upload,
            service,
            file_uuid,
            path
        )
    except HttpError as error:
        logger.info(f'{datetime.now()}|An error occured: {error}')
        return error


def download_file(path, file_uuid, google_cloud_api, logger):
    try:
        files_on_cloud = list_files()['files']

        for file in files_on_cloud:
            if file['name'] == file_uuid:
                google_cloud_api.download(service, file['id'], path, file_uuid)
    except HttpError as error:
        logger.error(f'{datetime.now()}|An error occured: {error}')
        return error
    logger.info(f"{datetime.now()}|File with uuid:{file_uuid} not found")
    return f"File with uuid:{file_uuid} not found"
                

def list_files():
    return service.files().list(
        pageSize=1000,
        fields="nextPageToken, files(id, name)"
    ).execute()
