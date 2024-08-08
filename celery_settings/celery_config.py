from celery import Celery

from settings.config import CONFIG

app = Celery()
app.conf.broker_url = CONFIG.CELERY_BROKER_STR
app.conf.update(broker_connection_retry_on_startup=True)

app.conf.timezone = 'UTC'

# celery -A celery_settings.celery_schedule worker -l info -P gevent
# celery -A celery_settings.celery_schedule beat
