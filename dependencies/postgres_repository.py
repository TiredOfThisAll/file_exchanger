from data_access.repository import Repository
from data_access.create_connection import create_connection
from settings.config import CONFIG


class PostgresRepository:
    singleton = Repository(create_connection(CONFIG.POSTGRE_CONNECTION_STR))

    @staticmethod
    def get_connection():
        return PostgresRepository.singleton.connection
    
    @staticmethod
    def create_db_if_not_exists():
        return PostgresRepository.singleton.create_db_if_not_exists()

    @staticmethod
    def create_schema_if_not_exists():
        PostgresRepository.singleton.create_schema_if_not_exists()

    @staticmethod
    def insert_new_metadata(metadata):
        PostgresRepository.singleton.insert_new_metadata(metadata)

    @staticmethod
    def get_metadata_by_uuid(uuid):
        return PostgresRepository.singleton.get_metadata_by_uuid(uuid)

    @staticmethod
    def get_all_metadata():
        return PostgresRepository.singleton.get_all_metadata()

    @staticmethod
    def delete_old_records(timestamp):
        PostgresRepository.singleton.delete_old_records(timestamp)
