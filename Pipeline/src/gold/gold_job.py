from dagster import AssetSelection, define_asset_job

from executors import get_executor_def
from .gold_assets import all_gold_assets


gold_job = define_asset_job(
    name="gold_datamart_job",
    selection=AssetSelection.assets(*all_gold_assets),
    executor_def=get_executor_def(),
)
