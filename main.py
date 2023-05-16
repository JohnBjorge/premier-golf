from premier_golf_scraper import PremierGolfScraper
from datetime import datetime, date, timedelta
from multiprocessing import Process, Pool, Queue, Manager, Lock, freeze_support
import json
from data_aggregator import DataAggregator
import concurrent.futures


def run_scraper(date_search):
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    pgs.start_driver()
    html = pgs.navigate_page()
    tee_times = pgs.scrape(html)
    results = pgs.get_tee_time_search_results(tee_times)
    pgs.save_to_json(results)
    pgs.quit()

if __name__ == "__main__":
    start_date = date.today()
    number_of_days = 2
    dates_list = [start_date + timedelta(days=i) for i in range(number_of_days)]

    max_workers = 6
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for day in dates_list:
            executor.submit(run_scraper, day)

    data_aggregator = DataAggregator()
    data_aggregator.aggregate_data()
    data_aggregator.save_data()
    data_aggregator.archive_data()

    # get setup with docker, devcontainer, codespace github, dotfiles, zsh4humans vs fish?
