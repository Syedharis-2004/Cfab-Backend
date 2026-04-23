"""
Celery application configuration.

Start the worker with:
    celery -A app.worker.celery_app worker --loglevel=info
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "check_yourself_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Prevent a single task from blocking a worker forever
    task_soft_time_limit=60,   # seconds — raises SoftTimeLimitExceeded
    task_time_limit=90,        # hard kill after 90 s
    task_acks_late=True,       # re-queue if worker crashes mid-task
    worker_prefetch_multiplier=1,  # fair dispatch
    task_always_eager=True,    # Run tasks synchronously locally without Redis
)
