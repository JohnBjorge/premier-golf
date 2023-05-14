from premier_golf_scraper import PremierGolfScraper
from datetime import datetime, date, timedelta
from multiprocessing import Process, Pool, Queue, Manager, Lock, freeze_support
import json
from data_aggregator import DataAggregator


def run_scraper(date_search, data_queue):
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    html = pgs.navigate_page()
    pgs.scrape(html)
    result = pgs.tee_time_summary_json()
    pgs.quit()
    data_queue.put(result)

def get_dates_range(start_day: str = date.today(), end_day: str = date.today() + timedelta(14)) -> list:
    if start_day < date.today():
        raise ValueError(f"start_day of {start_day} must be greater than or equal to today")
    if end_day > date.today() + timedelta(14):
        raise ValueError(f"end_day of {end_day} must be less than two weeks out from today")
    if start_day > end_day:
        raise ValueError(f"start_day of {start_day} must be less than end_day of {end_day}")

    dates_list = []
    day_range = end_day - start_day
    for day in range(day_range.days):
        dates_list.append(start_day + timedelta(days=day))
    return dates_list

if __name__ == "__main__":
    start_day = date.today() + timedelta(days=1)
    end_day = start_day + timedelta(days=2)
    dates_list = get_dates_range(start_day, end_day)

    data_queue = Queue()

    # create a list to hold the processes
    processes = []

    # start a new process for each URL
    for date in dates_list:
        process = Process(target=run_scraper, args=(date, data_queue))
        process.start()
        processes.append(process)

    # wait for all processes to complete
    for process in processes:
        process.join()

    data_aggregator = DataAggregator()
    for _ in range(len(dates_list)):
        data_aggregator.add_data(data_queue.get())

    with open("./sample/test.json", "w") as outfile:
        json.dump(data_aggregator.get_data(), outfile, indent=4)


