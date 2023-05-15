import json

class DataAggregator:
    def __init__(self):
        self.data = {}
        self.data["tee_times"] = list()

    # read json from directory and build tee times dictionary
    def add_data(self, new_data: dict):
        self.data["tee_times"].append(new_data)

    def get_data(self):
        return self.data

    def save_data(self):
        date_formatted = self.scrape_time.strftime("%Y%m%d")
        time_formatted = self.scrape_time.strftime("%H%M%S")
        filename = self.scrape_time.strftime("%Y%m%d%H%M%S")

        with open(f"./sample/aggregator/{date_formatted}/{time_formatted}/{filename}.json", "w") as outfile:
            json.dump(self.get_data(), outfile, indent=4)
