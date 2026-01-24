import json


class DataProvider:
    def __init__(self, filename):
        with open(filename) as file:
            self.data = json.load(file)

    def get(self, key):
        return self.data.get(key)
