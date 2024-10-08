import unittest
from datetime import datetime
import os
import logging
from fastapi.testclient import TestClient

from app.dependencies.drive_persistence import DrivePersistence
from app.dependencies.google_cloud_api import GoogleCloudApi
from app.dependencies.postgres_repository import PostgresRepository
from app.dependencies.sqlite_repository import SqliteRepository
from app.dependencies.main_logger import MainLogger
from main import app
from data.data_access.models import data
from data.data_classes.metadata import Metadata
from settings.config import CONFIG


client = TestClient(app)

SqliteRepository.create_db_if_not_exists()
data.drop(bind=SqliteRepository.get_connection())
SqliteRepository.create_schema_if_not_exists()


# Mock class to simulate file operations
class MockFile:
    def __init__(self):
        self.bytes_written = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def write(self, content):
        self.bytes_written += len(content)

# Mock class to simulate file persistence system
class TestPersistence:
    def __init__(self):
        TestPersistence.instance = self

    def open(self, path):
        self.mock_file = MockFile()
        return self.mock_file

# Mock class to simulate cloud API
class TestCloudApi:
    def upload(self, service, file_name, file_path):
        pass

    def download(self, service, google_file_id, path, file_uuid):
        pass


class TestLogger:
    @staticmethod
    def debug(msg):
        pass

    @staticmethod
    def info(msg):
        pass

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def error(msg):
        pass

    @staticmethod
    def critical(msg):
        pass


class TestFilePersistence(unittest.TestCase):
    def test_upload_file(self):
        app.dependency_overrides[DrivePersistence] = TestPersistence
        app.dependency_overrides[GoogleCloudApi] = TestCloudApi
        app.dependency_overrides[PostgresRepository] = SqliteRepository
        app.dependency_overrides[MainLogger] = TestLogger

        logging.disable(logging.CRITICAL + 1)

        with open("test.txt", "rb") as f:
            expected_file_length = len(f.read())
            response = client.post(
                "/api/upload-file/",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        actual_file_length = TestPersistence.instance.mock_file.bytes_written
        self.assertEqual(expected_file_length, actual_file_length)

    def test_download_file(self):
        app.dependency_overrides[GoogleCloudApi] = TestCloudApi
        app.dependency_overrides[PostgresRepository] = SqliteRepository
        app.dependency_overrides[MainLogger] = TestLogger

        logging.disable(logging.CRITICAL + 1)

        uuid = "1d2ea29b-dcb9-4e12-a216-b6288f98a5b6"

        test_file_path = os.path.join(CONFIG.FILES_PATH, uuid)

        if not os.path.exists(test_file_path):
            with open("test.txt") as f:
                content = f.read()
                filesize = len(content)

            with open(test_file_path, 'w') as f:
                f.write(content)
        else:
            with open(test_file_path) as f:
                filesize = len(f.read())

        metadata = Metadata(uuid,
            "test",
            filesize,
            "text/plain",
            ".txt",
            datetime(2024, 8, 6, 14, 6, 19, 560894)
        )

        # {'id': 1, 'uuid': '1d2ea29b-dcb9-4e12-a216-b6288f98a5b6', 'name': 'test', 'size': '2696', 'format': 'text/plain', 'extension': '.txt', 'was_uploaded_on': datetime.datetime(2024, 8, 6, 14, 6, 19, 560894)}
        SqliteRepository.insert_new_metadata(metadata)

        with open(test_file_path, "rb") as f:
            expected_file_length = len(f.read())
            response = client.get(f"/api/download-file/{uuid}")

        self.assertEqual(expected_file_length, response.num_bytes_downloaded)
