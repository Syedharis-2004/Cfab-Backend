import os
from celery import Celery

REDIS_URL = "redis://localhost:6379/0"
celery_app = Celery("test_app", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="test_task")
def test_task():
    return "success"

if __name__ == "__main__":
    try:
        print(f"Connecting to Redis at {REDIS_URL}...")
        res = test_task.delay()
        print(f"Task dispatched! Task ID: {res.id}")
    except Exception as e:
        print(f"FAILED: {e}")
