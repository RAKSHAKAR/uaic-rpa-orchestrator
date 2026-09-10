"""Celery Application and Distributed Task Queue Configuration."""

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

from app.core.config import settings

celery_app = Celery(
    "uaic_claim_orchestrator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
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
            "schedule": crontab(minute=0, hour="*/12"),  # Every 12 hours (configurable)
            "args": (),
        },
    },
)
