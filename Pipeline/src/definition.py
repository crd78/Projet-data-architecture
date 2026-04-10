from dagster import Definitions
from Bronze.Ingestion import all_ingestion_assets, ingestion_job

defs = Definitions(
    assets=all_ingestion_assets,
    jobs=[ingestion_job] if ingestion_job is not None else [],
)