import json
import shutil
import os

class DataAggregator:
    def __init__(self):
        self.data = {}
        self.data["tee_times"] = list()

    # read json from directory and build tee times dictionary
    def aggregate_data(self):
        # spin through scraper directories combining into single json file
        # self.data["tee_times"].append(new_data)

        directory = "./sample/scraper"  # Specify the path to your directory

        # Recursively search for JSON files in the directory and its subdirectories
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".json"):
                    filepath = os.path.join(root, filename)
                    with open(filepath, "r") as file:
                        data = json.load(file)
                        self.data["tee_times"].append(data)


    def get_data(self):
        return self.data

    def save_data(self):
        # date_formatted = self.scrape_time.strftime("%Y%m%d")
        # time_formatted = self.scrape_time.strftime("%H%M%S")
        # file_name = self.scrape_time.strftime("%Y%m%d%H%M%S")

        # todo: figure out directory structure and naming
        date_formatted = "test_data"
        time_formatted = "test_time"
        file_name = "test_file_name"

        # todo: make file path a class variable?
        file_path = f"./sample/aggregator/{date_formatted}/{time_formatted}/"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(f"{file_path}/{file_name}.json", "w") as outfile:
            json.dump(self.data, outfile, indent=4)

    def archive_data(self):
        source_directory = "./sample/scraper"
        destination_directory = "./sample/archive/scraper"

        for root, dirs, files in os.walk(source_directory):
            for filename in files:
                source_path = os.path.join(root, filename)
                relative_path = os.path.relpath(source_path, source_directory)
                destination_path = os.path.join(destination_directory, relative_path)
                
                if os.path.exists(destination_path):
                    # If the destination path already exists, use the destination directory
                    destination_path = os.path.join(destination_path, filename)
                
                # Copy the file to the destination path
                shutil.move(source_path, destination_path)