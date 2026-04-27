from dagster import (
    Definitions,
    ScheduleDefinition,
    RunRequest,
    RunStatusSensorContext,
    DagsterRunStatus,
    run_status_sensor,
)
from dagster_celery import celery_executor
from Bronze.Ingestion import all_ingestion_assets, ingestion_job
from Silver.preprocessing import all_preprocessing_assets, preprocessing_job

# Bronze tourne tous les jours à minuit
bronze_daily_schedule = ScheduleDefinition(
    name="bronze_daily_schedule",
    job=ingestion_job,
    cron_schedule="0 0 * * *",
)

# Silver se déclenche automatiquement dès que Bronze termine avec succès
@run_status_sensor(
    name="silver_after_bronze_sensor",
    run_status=DagsterRunStatus.SUCCESS,
    monitored_jobs=[ingestion_job],
    request_job=preprocessing_job,
)
def silver_after_bronze_sensor(context: RunStatusSensorContext):
    return RunRequest(run_key=context.dagster_run.run_id)


defs = Definitions(
    assets=all_ingestion_assets + all_preprocessing_assets,
    jobs=[ingestion_job, preprocessing_job],
    chedules=[bronze_daily_schedule],
    sensors=[silver_after_bronze_sensor],
    executor=celery_executor.configured(
        {
            "broker": "redis://redis:6379/0",
            "backend": "redis://redis:6379/0",
        }
    ),
    
)