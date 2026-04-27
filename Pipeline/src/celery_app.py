from celery import Celery
from dagster_celery.tasks import create_task

celery_app = Celery(
    "dagster_pipeline",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

# Register Dagster's execution task on this app so workers can consume step tasks.
execute_plan = create_task(celery_app)