from premier_golf_scraper import PremierGolfScraper
from datetime import datetime, date, timedelta
from multiprocessing import Process, Manager, Lock, freeze_support
import json

# Crossroads seems scuffed (same day only)
# Interbay is 9 holes only
# Ocean Shores also displays cart fee on first page

def run_scraper(date_search, shared_dict, lock):
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    html = pgs.navigate_page()
    pgs.scrape(html)

    lock.acquire()

    tee_time_search = {}
    tee_time_search["scrape_time"] = pgs.scrape_time
    tee_time_search["date_search"] = pgs.date_search
    tee_time_search["time_search"] = pgs.time_search
    tee_time_search["course_search"] = pgs.course_search
    tee_time_search["players_search"] = pgs.players_search
    tee_time_search["hole_search"] = pgs.hole_search
    tee_time_search["tee_times"] = pgs.tee_times

    shared_dict["tee_times"] += [tee_time_search]

    lock.release()

def get_dates_range(start_day: str = date.today(), end_day: str = date.today() + timedelta(14)) -> list:
    if start_day < date.today():
        raise ValueError(f"start_day of {start_day} must be greater than or equal to today")
    if end_day > date.today() + timedelta(14):
        raise ValueError(f"end_day of {end_day} must be less than two weeks out from today")
    if start_day > end_day:
        raise ValueError(f"start_day of {start_day} must be less than end_day of {end_day}")

    dates_list = []
    day_range = end_day - start_day
    for day in range(day_range):
        dates_list.append(start_day + timedelta(days=day))
    return dates_list

if __name__ == "__main__":
    dates_list = get_dates_range()

    freeze_support()

    manager = Manager()
    shared_dict = manager.dict()

    shared_dict["tee_times"] = list()
    lock = Lock()

    # create a list to hold the processes
    processes = []

    # start a new process for each URL
    for date in dates_list:
        process = Process(target=run_scraper, args=(date, shared_dict, lock))
        process.start()
        processes.append(process)

    # wait for all processes to complete
    for process in processes:
        process.join()

    tee_times = dict(shared_dict)

    with open("test.json", "w") as outfile:
        json.dump(tee_times, outfile)


# {
#     tee_times: [
#         {
#             scrape time:
#             date_search:
#             tee_time: [ {course,
#                           time,
#                           players,
#                           price
#                           },
#             ]
#         },
#         {
#             scrape time:
#             date_search:
#             tee_time: [ {course,
#                           time,
#                           players,
#                           price
#                           },
#             ]
#         }
#     ]
# }
