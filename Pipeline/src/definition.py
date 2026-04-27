from dagster import Definitions, ScheduleDefinition
from dagster_celery import celery_executor
from Bronze.Ingestion import all_ingestion_assets, ingestion_job
from Silver.preprocessing import all_preprocessing_assets, preprocessing_job

weekly_ingestion_schedule = ScheduleDefinition(
    job=ingestion_job,
    cron_schedule="0 2 * * 1",
    execution_timezone="Europe/Paris",
)

weekly_preprocessing_schedule = ScheduleDefinition(
    job=preprocessing_job,
    cron_schedule="30 2 * * 1",
    execution_timezone="Europe/Paris",
)

defs = Definitions(
    assets=all_ingestion_assets + all_preprocessing_assets,
    jobs=[job for job in [ingestion_job, preprocessing_job] if job is not None],
    schedules=[weekly_ingestion_schedule, weekly_preprocessing_schedule],
    executor=celery_executor.configured(
        {
            "broker": "redis://redis:6379/0",
            "backend": "redis://redis:6379/0",
        }
    ),
)