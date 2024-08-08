from data_access.repository import Repository
from data_access.create_connection import create_connection
from settings.config import CONFIG


class SqliteRepository:
    singleton = Repository(create_connection(CONFIG.SQLITE_CONNECTION_STR))

    @staticmethod
    def get_connection():
        return SqliteRepository.singleton.connection
    
    @staticmethod
    def create_db_if_not_exists():
        return SqliteRepository.singleton.create_db_if_not_exists()

    @staticmethod
    def create_schema_if_not_exists():
        SqliteRepository.singleton.create_schema_if_not_exists()

    @staticmethod
    def insert_new_metadata(metadata):
        SqliteRepository.singleton.insert_new_metadata(metadata)

    @staticmethod
    def get_metadata_by_uuid(uuid):
        return SqliteRepository.singleton.get_metadata_by_uuid(uuid)

    @staticmethod
    def get_all_metadata():
        return SqliteRepository.singleton.get_all_metadata()

    @staticmethod
    def delete_old_records(timestamp):
        SqliteRepository.singleton.delete_old_records(timestamp)
