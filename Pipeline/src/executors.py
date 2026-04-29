import os


def get_executor_def():
    if os.getenv("DAGSTER_USE_CELERY", "0").lower() not in {"1", "true", "yes"}:
        return None

    try:
        from dagster_celery import celery_executor
    except ImportError:
        return None

    broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    try:
        return celery_executor.configured(
            {
                "broker": broker,
                "backend": backend,
                "config_source": {
                    "task_default_queue": os.getenv("CELERY_DEFAULT_QUEUE", "dagster"),
                    "worker_prefetch_multiplier": 1,
                    "task_acks_late": True,
                },
            }
        )
    except Exception:
        return None
