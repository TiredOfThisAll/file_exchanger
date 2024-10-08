import json
import os


class Config:
    def __init__(self) -> None:
        self.PROJECT_PATH = os.getcwd()

        with open(os.path.join(self.PROJECT_PATH, "settings", "config.json")) as f:
            config_dict = json.load(f)

        self.POSTGRE_CONNECTION_STR = config_dict["postgre_connection_str"]
        self.SQLITE_CONNECTION_STR = config_dict["sqlite_connection_str"]
        self.CELERY_BROKER_STR = config_dict["celery_broker_str"]
        self.DATABASE = config_dict["database"]

        # the path must be relative to the root folder of the project
        self.FILES_PATH = os.path.join(
            self.PROJECT_PATH,
            config_dict["files_dir_path"]
        )
        self.GOOGLE_API_KEY_PATH = os.path.join(
            self.PROJECT_PATH,
            config_dict["google_api_key_path"]
        )
        self.LOGS_PATH = os.path.join(
            self.PROJECT_PATH,
            config_dict["logs_dir_path"]
        )
        self.LOGS_FILE_NAME = config_dict["logs_file_name"]

        self.MAX_FILE_SIZE = config_dict["max_file_size"]

CONFIG = Config()
