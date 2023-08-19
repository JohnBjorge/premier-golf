from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_package_module,
)

from . import assets

all_assets = load_assets_from_package_module(assets)

golf_scraper_job = define_asset_job("golf_scraper_job", selection=AssetSelection.groups("golf"))

golf_scraper_schedule = ScheduleDefinition(
    job=golf_scraper_job,
    cron_schedule="0 * * * *",  # every hour
)

defs = Definitions(
    assets=all_assets,
    schedules=[golf_scraper_schedule],
)
