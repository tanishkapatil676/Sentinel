import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = Redis.from_url(REDIS_URL)
job_queue = Queue("sentinel-jobs", connection=redis_client)
