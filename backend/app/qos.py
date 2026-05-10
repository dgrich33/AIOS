from datetime import datetime
import json
import time
from threading import Lock

import redis
from sqlalchemy.orm import Session

from .config import get_settings
from .models import QosJob, User
from .observability import QOS_JOBS_COMPLETED_TOTAL, QOS_JOBS_TOTAL, QOS_QUEUE_DEPTH


_memory_lock = Lock()
_memory_queue: list[tuple[float, str]] = []


def _redis_client():
    settings = get_settings()
    if not settings.redis_url:
        return None
    try:
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return client
    except redis.RedisError:
        return None


def _priority_score(priority_class: str) -> int:
    return {
        "premium_unlimited": 10,
        "developer": 30,
        "standard": 50,
        "background": 90,
    }.get(priority_class, 50)


def enqueue_job(db: Session, user: User, job_type: str, payload: dict, priority_class: str = "premium_unlimited") -> QosJob:
    job = QosJob(
        user_id=user.id,
        job_type=job_type,
        priority_class=priority_class,
        payload=json.dumps(payload),
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    score = _priority_score(priority_class) + time.time() / 1_000_000
    client = _redis_client()
    if client:
        client.zadd("aios:qos:queue", {job.id: score})
        QOS_QUEUE_DEPTH.set(client.zcard("aios:qos:queue"))
    else:
        with _memory_lock:
            _memory_queue.append((score, job.id))
            _memory_queue.sort(key=lambda item: item[0])
            QOS_QUEUE_DEPTH.set(len(_memory_queue))
    QOS_JOBS_TOTAL.labels(priority_class=priority_class).inc()
    return job


def queue_depth() -> int:
    client = _redis_client()
    if client:
        depth = int(client.zcard("aios:qos:queue"))
    else:
        with _memory_lock:
            depth = len(_memory_queue)
    QOS_QUEUE_DEPTH.set(depth)
    return depth


def pop_next_job_id() -> str | None:
    client = _redis_client()
    if client:
        popped = client.zpopmin("aios:qos:queue", 1)
        QOS_QUEUE_DEPTH.set(client.zcard("aios:qos:queue"))
        return popped[0][0] if popped else None
    with _memory_lock:
        if not _memory_queue:
            QOS_QUEUE_DEPTH.set(0)
            return None
        _, job_id = _memory_queue.pop(0)
        QOS_QUEUE_DEPTH.set(len(_memory_queue))
        return job_id


def process_one(db: Session) -> QosJob | None:
    job_id = pop_next_job_id()
    if not job_id:
        return None
    job = db.query(QosJob).filter(QosJob.id == job_id).first()
    if not job:
        return None
    job.status = "running"
    job.started_at = datetime.utcnow()
    db.commit()

    payload = json.loads(job.payload or "{}")
    job.result = json.dumps(
        {
            "message": "Local QoS worker processed job",
            "jobType": job.job_type,
            "objective": payload.get("objective", ""),
            "adapter": "LocalQueueCodexAdapter",
        }
    )
    job.status = "completed"
    job.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    QOS_JOBS_COMPLETED_TOTAL.labels(priority_class=job.priority_class).inc()
    return job
