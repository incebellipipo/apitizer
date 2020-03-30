from pymongo import MongoClient


class DatabaseUpdater:
    def __init__(self):
        self.client = MongoClient()

        self.db = self.client['covid']
        self.collection = self.db.data