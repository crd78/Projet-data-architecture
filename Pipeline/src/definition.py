from dagster import Definitions
from Bronze.Ingestion import all_ingestion_assets, ingestion_job
from Silver.preprocessing import all_preprocessing_assets, preprocessing_job

defs = Definitions(
    assets=all_ingestion_assets + all_preprocessing_assets,
    jobs=[job for job in [ingestion_job, preprocessing_job] if job is not None],
)

