from celery.schedules import crontab

from celery_settings.celery_config import app

# Import the task module to ensure tasks are registered
from tasks import clear_db

# Scheedule job to run clear_old_files task everyday at midnight
app.conf.beat_schedule = {
    'run-my-job-daily': {
        'task': 'tasks.clear_db.clear_old_files',
        'schedule': crontab(minute="*"),
    },
}
