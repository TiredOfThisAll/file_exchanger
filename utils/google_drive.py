from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, HttpError
import asyncio
import os
import io


service = build(
    'drive',
    'v3',
    credentials=service_account.Credentials.from_service_account_file(
        filename= os.path.join('settings', 'google_drive_api_key.json'),
        scopes=['https://www.googleapis.com/auth/drive']
))


def upload_file(path, file_uuid, google_cloud_api):
    asyncio.get_event_loop().run_in_executor(
        None,
        google_cloud_api.upload,
        service,
        file_uuid,
        path
    )


def download_file_from_cloud(google_file_id, path, file_uuid):
    try:
        request_file = service.files().get_media(fileId=google_file_id)
        file = io.FileIO(os.path.join(path, file_uuid), mode='wb')
        downloader = MediaIoBaseDownload(file, request_file)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
    except HttpError as error:
        print(F'An error occurred: {error}')


def download_file(path, file_uuid):
    files_on_cloud = list_files()['files']

    for file in files_on_cloud:
        if file['name'] == file_uuid:
            download_file_from_cloud(file['id'], path, file_uuid)
            return
    return "File not found"
                

def list_files():
    return service.files().list(
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
    ).execute()
