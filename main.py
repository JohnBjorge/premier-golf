from premier_golf_scraper import PremierGolfScraper
from datetime import datetime, date, timedelta
from multiprocessing import Process, Pool, Queue, Manager, Lock, freeze_support
import json
from data_aggregator import DataAggregator


def run_scraper(date_search):
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    pgs.start_driver()
    html = pgs.navigate_page()
    tee_times = pgs.scrape(html)
    results = pgs.get_tee_time_search_results(tee_times)
    pgs.save_to_json(results)
    pgs.quit()

def get_dates_range(start_day: date = date.today(), end_day: date = date.today() + timedelta(14)) -> list:
    dates_list = []
    day_range = end_day - start_day
    for day in range(day_range.days):
        dates_list.append(start_day + timedelta(days=day))
    return dates_list

if __name__ == "__main__":
    start_day = date.today()
    end_day = start_day + timedelta(days=2)
    dates_list = get_dates_range(start_day, end_day)

    # consider using threads instead of processes

    # create a list to hold the processes
    processes = []

    # start a new process for each URL
    for day in dates_list:
        process = Process(target=run_scraper, args=(day,))
        process.start()
        processes.append(process)

    # wait for all processes to complete
    for process in processes:
        process.join()

    data_aggregator = DataAggregator()
    # for file in files that I generated in sample directory
    for _ in range(len(dates_list)):
        print("es")
        # data_aggregator.add_data(data_queue.get())

    # call data_aggregator.save_data()




    # get setup with docker, devcontainer, codespace github, dotfiles, zsh4humans vs fish?
