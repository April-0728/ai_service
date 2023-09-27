import os

import pymongo


class MongoDriver:
    def __init__(self, mongo_uri: str = None):
        if mongo_uri is None:
            self.mongo_uri = os.environ.get("MONGODB_URL")
        else:
            self.mongo_uri = mongo_uri
        self.client = None

    def __enter__(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def query_collection(self, collection_name, query):
        with self as client:
            db = client.get_database()
            collection = db.get_collection(collection_name)
            return list(collection.find(query))
