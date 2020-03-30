from pymongo import MongoClient


class DatabaseController:
    def __init__(self):
        self.client = MongoClient()

        self.db = self.client['covid']
        self.collection = self.db['data']

        print(self.client.list_database_names())

    def find(self):
        return self.collection.find()

    def find_one(self, obj=None):
        return self.collection.find_one(obj, sort=[('_id', -1)])

    def insert(self, obj):
        self.collection.insert_one(obj)

    def update(self, _id, obj):
        _good = True
        for _, val in obj.items():
            if val is None:
                _good = False
        if _good:
            query = {"_id": _id}
            self.collection.update(query, obj)

    def insert_or_update(self, obj):
        _good = True
        for _, val in obj.items():
            if val is None:
                _good = False
        if not _good:
            return

        query = {"publication_date": obj["publication_date"]}
        lookup_result = self.collection.find_one(query)
        if lookup_result is not None:
            self.update(lookup_result["_id"], obj)
        else:
            self.insert(obj)
