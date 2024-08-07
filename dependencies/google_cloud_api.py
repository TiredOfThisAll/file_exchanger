from googleapiclient.http import MediaFileUpload


class GoogleCloudApi:
    def upload(self, service, file_name, file_path):
        service.files().create(body={'name': file_name}, media_body=MediaFileUpload(file_path), fields='id').execute()
