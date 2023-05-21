from premier_golf_scraper import PremierGolfScraper
from datetime import datetime, date, timedelta
from multiprocessing import Process, Pool, Queue, Manager, Lock, freeze_support
import json
from data_aggregator import DataAggregator
import concurrent.futures
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner


def run_scraper(date_search):
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    pgs.start_driver()
    html = pgs.navigate_page()
    tee_times = pgs.scrape(html)
    results = pgs.get_tee_time_search_results(tee_times)
    pgs.save_to_json(results)
    pgs.quit()

@task()
def threaded_scrape(dates_list, max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for day in dates_list:
            executor.submit(run_scraper, day)

@task()
def aggregate_data(data_aggregator):
    data_aggregator.aggregate_data()
    data_aggregator.save_data()

@task()
def upload_to_gcs(data_aggregator):
    data_aggregator.upload_to_google()


@flow(task_runner=SequentialTaskRunner())
def scrape_to_gcs(dates_list, max_workers):
    threaded_scrape.submit(dates_list, max_workers)
    data_aggregator = DataAggregator()
    aggregate_data.submit(data_aggregator)
    upload_to_gcs.submit(data_aggregator)

if __name__ == "__main__":
    start_date = date.today()
    number_of_days = 2

    dates_list = [start_date + timedelta(days=i) for i in range(number_of_days)]

    max_workers = 6
    scrape_to_gcs(dates_list, max_workers)

    # get setup with docker, devcontainer, codespace github, dotfiles, zsh4humans vs fish?
