from celery import Celery

app = Celery()
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.update(broker_connection_retry_on_startup=True)

app.conf.timezone = 'UTC'

# celery -A celery_settings.celery_schedule worker -l info -P gevent
# celery -A celery_settings.celery_schedule beat
