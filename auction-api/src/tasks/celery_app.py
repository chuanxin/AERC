from celery import Celery
from src.config.settings import REDIS_URL

celery_app = Celery(
    "auction",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    task_track_started=True,
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=REDIS_URL,
)

celery_app.autodiscover_tasks([
    "src.tasks.auction_tasks",
    "src.tasks.notification_tasks",
])
