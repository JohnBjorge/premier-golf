import json
import shutil
import os

class DataAggregator:
    def __init__(self):
        self.data = {}
        self.data["tee_times"] = list()
        self.load_date = None
        self.min_load_time = None
        self.max_load_time = None


    # change directory structure to the following:
    """
    data
        aggregator
            date
                mintimemaxtime.json
            archive
                date
                    mintimemaxtime
                        mintimemaxtime.json
        scraper
            date
                scrapedatetime.json
            archive
                date
                    mintimemaxtime
                        scrapedatetime.json

    """

    # read json from directory and build tee times dictionary
    def aggregate_data(self):

        root = "./data/scraper"

        for dirpath, dirnames, filenames in os.walk(root):
            if "archive" in dirnames:
                dirnames.remove("archive")

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                self.load_date = filename[:8]
                self.min_load_time = min(filenames)[:-5]
                self.max_load_time = max(filenames)[:-5]
                with open(filepath, "r") as file:
                    data = json.load(file)
                    self.data["tee_times"].append(data)


    def get_data(self):
        return self.data

    def save_data(self):
        date = self.load_date
        time_range = "_".join([self.min_load_time, self.max_load_time])

        file_path = f"./data/aggregator/{date}/"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(f"{file_path}/{time_range}.json", "w") as outfile:
            json.dump(self.data, outfile, indent=4)

        #archive scraper data if agg successful
        self.archive_data(source_directory="./data/scraper", destination_directory="./data/scraper/archive")
        
    def archive_data(self, source_directory, destination_directory):
        time_range = "_".join([self.min_load_time, self.max_load_time])
        destination_directory = "/".join([destination_directory, self.load_date, time_range])

        for item in os.listdir(source_directory):
            if item != "archive":
                item_path = os.path.join(source_directory, item)
                if os.path.isdir(item_path):
                    shutil.move(item_path, destination_directory)

    def upload_to_google(self):
        # upload agg to google 
            # do it

        # archive agg data if upload successful
        self.archive_data(source_directory="./data/aggregator", destination_directory="./data/aggregator/archive")
        