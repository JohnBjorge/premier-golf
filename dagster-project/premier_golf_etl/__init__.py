from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_package_module,
)

from . import assets

all_assets = load_assets_from_package_module(assets)

premier_golf_scraper_job = define_asset_job("premier_golf_scraper_job", selection=AssetSelection.groups("golf"))

premier_golf_schedule = ScheduleDefinition(
    job=premier_golf_scraper_job,
    cron_schedule="*/30 * * * *",  # every 30min
)

defs = Definitions(
    assets=all_assets,
    schedules=[premier_golf_schedule],
)
