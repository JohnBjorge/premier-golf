class DataAggregator:
    def __init__(self):
        self.data = {}
        self.data["tee_times"] = list()

    def add_data(self, new_data: dict):
        self.data["tee_times"].append(new_data)

    def get_data(self):
        return self.data

    def save_data(self):
        pass