from celery import Celery
from src.config import Config


celery_app=Celery(
    "tasks",
    broker=getattr(Config, "REDIS_URL", "redis://localhost:6379/0"),
    backend=getattr(Config, "REDIS_URL", "redis://localhost:6379/0"),
    include=["src.worker.email_worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
