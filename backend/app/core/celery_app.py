"""Celery Application and Distributed Task Queue Configuration."""

from celery import Celery
from kombu import Exchange, Queue

import app.compat  # noqa: F401
from app.core.config import settings

celery_app = Celery(
    "uaic_claim_orchestrator",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
    include=[
        "app.tasks.ingest_tasks",
        "app.tasks.scraper_tasks",
        "app.tasks.fuzzy_tasks",
        "app.tasks.retry_tasks",
        "app.tasks.queue_runner",
        "app.tasks.export_tasks",
        "app.tasks.notification_tasks",
    ],
)

# Define Exchanges
default_exchange = Exchange("default", type="direct")
ingest_exchange = Exchange("ingest", type="direct")
scrapers_exchange = Exchange("scrapers", type="direct")
matcher_exchange = Exchange("matcher", type="direct")
notifications_exchange = Exchange("notifications", type="direct")

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=86400,  # 24 hours
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
    broker_connection_timeout=15.0,
    broker_transport_options={"socket_timeout": 30.0, "socket_connect_timeout": 15.0},
    result_backend_max_retries=0,
    result_backend_transport_options={"max_retries": 0, "retry_policy": {"max_retries": 0}},
    redis_backend_transport_options={"max_retries": 0, "retry_policy": {"max_retries": 0}},
    
    # Define Dedicated Queues
    task_queues=(
        Queue("default", default_exchange, routing_key="default"),
        Queue("ingest", ingest_exchange, routing_key="ingest"),
        Queue("scrapers", scrapers_exchange, routing_key="scrapers"),
        Queue("matcher", matcher_exchange, routing_key="matcher"),
        Queue("notifications", notifications_exchange, routing_key="notifications"),
    ),
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Monitoring and Flower Event Support
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Route tasks to dedicated queues
    task_routes={
        "app.tasks.ingest_tasks.*": {"queue": "ingest"},
        "app.tasks.scraper_tasks.*": {"queue": "scrapers"},
        "app.tasks.fuzzy_tasks.*": {"queue": "matcher"},
        "app.tasks.retry_tasks.*": {"queue": "default"},
        "app.tasks.queue_runner.*": {"queue": "default"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Celery Beat Periodic Schedules
    beat_schedule={
        "advance-auto-queue-periodic": {
            "task": "app.tasks.queue_runner.advance_auto_queue_task",
            "schedule": 60.0,  # Active heartbeat every 60 seconds to advance pending claim batches
            "args": (),
        },
        "retrigger-failed-cases-periodic": {
            "task": "app.tasks.retry_tasks.retrigger_failed_cases_task",
            "schedule": 60.0,  # Runtime settings control retry delay and limits.
            "args": (),
        },
        "dispatch-due-email-digests": {
            "task": "app.tasks.notification_tasks.dispatch_due_digests_task",
            "schedule": 60.0,
            "args": (),
        },
    },
)


@celery_app.on_after_configure.connect
def setup_worker_startup(**kwargs):
    """Clean stale concurrency locks when celery worker starts up."""
    import logging

    import redis as redis_lib
    _log = logging.getLogger("uaic_orchestrator.celery")
    try:
        r = redis_lib.Redis.from_url(settings.CELERY_BROKER_URL or settings.REDIS_URL)
        r.delete("uaic:browser:active_count")
        _log.info("[Celery] Reset uaic:browser:active_count concurrency lock on worker boot.")
    except Exception as e:
        _log.warning(f"[Celery] Could not reset browser semaphore on boot: {e}")
