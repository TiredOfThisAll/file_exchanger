from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, HttpError
import io
import os
from datetime import datetime


class GoogleCloudApi:
    def upload(self, service, file_name, file_path):
        service.files().create(body={'name': file_name}, media_body=MediaFileUpload(file_path), fields='id').execute()
    
    def download(self, service, google_file_id, path, file_uuid):
        request_file = service.files().get_media(fileId=google_file_id)
        file = io.FileIO(os.path.join(path, file_uuid), mode='wb')
        downloader = MediaIoBaseDownload(file, request_file)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
