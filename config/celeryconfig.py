import os

from celery.schedules import crontab
from django.conf import settings
from kombu import Queue


broker_url = settings.CELERY_BROKER_URL
timezone = "Asia/Seoul"

broker_transport_options = {
    "max_retries": 1,
    "interval_start": 0,  # celery client 에서 broker 찾지 못할 시 즉시 exception
    "visibility_timeout": 86400,  # 초단위
}

imports = (  # app 내의 tasks 경로 설정
    "llm.tasks",
)

task_queues = {
    Queue("default", routing_key="default"),
}

task_default_queue = "default"
task_default_priority = 5  # range: 0 ~ 9

beat_schedule = {

}
