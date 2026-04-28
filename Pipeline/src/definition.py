from dagster import (
    Definitions,
    ScheduleDefinition,
    RunRequest,
    RunStatusSensorContext,
    DagsterRunStatus,
    run_status_sensor,
)
from Bronze.Ingestion import all_ingestion_assets, ingestion_job
from Silver.preprocessing import all_preprocessing_assets, preprocessing_job
from gold.gold_job import all_gold_assets, gold_job


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


# Gold se déclenche automatiquement dès que Silver termine avec succès
@run_status_sensor(
    name="gold_after_silver_sensor",
    run_status=DagsterRunStatus.SUCCESS,
    monitored_jobs=[preprocessing_job],
    request_job=gold_job,
)
def gold_after_silver_sensor(context: RunStatusSensorContext):
    return RunRequest(run_key=context.dagster_run.run_id)


defs = Definitions(
    assets=all_ingestion_assets + all_preprocessing_assets + all_gold_assets,
    jobs=[ingestion_job, preprocessing_job, gold_job],
    schedules=[bronze_daily_schedule],
    sensors=[silver_after_bronze_sensor, gold_after_silver_sensor],
)