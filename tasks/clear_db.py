from datetime import datetime, timedelta
from celery.utils.log import get_task_logger

from data.data_access.repository import Repository
from data.data_access.create_connection import create_connection
from celery_settings.celery_config import app
from settings.config import CONFIG

repository = Repository(create_connection(CONFIG.POSTGRE_CONNECTION_STR))


logger = get_task_logger(__name__)

@app.task
def clear_old_files():
    logger.info("Task ran")

    current_time = datetime.now()
    timestamp = current_time - timedelta(days=1)
    
    error = repository.delete_old_records(timestamp)
    if error:
        logger.error(error)
    logger.info("Task done")
