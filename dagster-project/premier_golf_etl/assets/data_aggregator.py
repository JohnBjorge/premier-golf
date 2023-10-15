import json
from pathlib import Path
import shutil
import os
from prefect_gcp.cloud_storage import GcsBucket

class DataAggregator:
    def __init__(self):
        self.data = {}
        self.data["tee_times"] = list()
        self.load_date = None
        self.min_load_time = None
        self.max_load_time = None
        self.agg_file_path = None


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

    def get_load_date_parts(self):
        year = self.load_date[:4]
        month = self.load_date[4:6]
        day = self.load_date[6:]
        return year, month, day

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

        self.agg_file_path = Path(f"{file_path}/{time_range}.json")
        with open(self.agg_file_path, "w") as outfile:
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
        # # Initialize a client to interact with Google Cloud Storage
        # storage_client = storage.Client()

        # # Get the bucket where you want to upload the JSON file
        # bucket = storage_client.bucket(bucket_name)

        # # Specify the name for the destination blob (object) in GCS
        # blob = bucket.blob(destination_blob_name)

        # # Upload the JSON file to GCS
        # blob.upload_from_filename(json_file_path)

        # # Example usage
        # json_file_path = '/path/to/your/jsonfile.json'
        # bucket_name = 'your-gcs-bucket-name'
        # destination_blob_name = 'destination/folder/your-jsonfile.json'

        # upload_to_gcs(json_file_path, bucket_name, destination_blob_name)


        # archive agg data if upload successful
        self.archive_data(source_directory="./data/aggregator", destination_directory="./data/aggregator/archive")
        