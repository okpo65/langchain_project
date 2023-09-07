from datetime import datetime

from celery import Celery

app = Celery(__name__)
app.config_from_object("config.celeryconfig")

app.autodiscover_tasks()

app.now = datetime.utcnow
